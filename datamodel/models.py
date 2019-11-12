from django.db import models
from django.contrib.auth.models import User
from enum import IntEnum
from django.core.exceptions import ValidationError

INVALID_CELL = 'Invalid cell for a cat or the mouse|Gato o ratón en posición no válida'


class GameStatus(IntEnum):
    CREATED = 0
    ACTIVE = 1
    FINISHED = 2

    def __str__(self):
        if self == GameStatus.CREATED:
            return 'Created'
        elif self == GameStatus.ACTIVE:
            return 'Active'
        elif self == GameStatus.FINISHED:
            return 'Finished'
        else:
            return 'Error'


class Game(models.Model):
    cat_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='games_as_cat'
    )
    mouse_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='games_as_mouse',
        null=True,
        blank=True
    )
    cat1 = models.IntegerField(default=0, null=False)
    cat2 = models.IntegerField(default=2, null=False)
    cat3 = models.IntegerField(default=4, null=False)
    cat4 = models.IntegerField(default=6, null=False)
    mouse = models.IntegerField(default=59, null=False)
    cat_turn = models.BooleanField(default=True, null=False)
    status = models.IntegerField(default=GameStatus.CREATED, null=False)

    MIN_CELL = 0
    MAX_CELL = 63

    def __init__(self, *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)
        self.validate()

    def save(self, *args, **kwargs):
        self.validate()
        if self.status is GameStatus.CREATED and self.mouse_user is not None:
            self.status = GameStatus.ACTIVE
        super(Game, self).save(*args, **kwargs)

    def validate(self):
        if self.cat1 < Game.MIN_CELL or self.cat1 > Game.MAX_CELL:
            raise ValidationError(INVALID_CELL)
        if self.cat2 < Game.MIN_CELL or self.cat2 > Game.MAX_CELL:
            raise ValidationError(INVALID_CELL)
        if self.cat3 < Game.MIN_CELL or self.cat3 > Game.MAX_CELL:
            raise ValidationError(INVALID_CELL)
        if self.cat4 < Game.MIN_CELL or self.cat4 > Game.MAX_CELL:
            raise ValidationError(INVALID_CELL)
        if self.mouse < Game.MIN_CELL or self.mouse > Game.MAX_CELL:
            raise ValidationError(INVALID_CELL)
        if self.cat1%2 != self.cat1//8%2:
            raise ValidationError(INVALID_CELL)
        if self.cat2%2 != self.cat2//8%2:
            raise ValidationError(INVALID_CELL)
        if self.cat3%2 != self.cat3//8%2:
            raise ValidationError(INVALID_CELL)
        if self.cat4%2 != self.cat4//8%2:
            raise ValidationError(INVALID_CELL)
        if self.mouse%2 != self.mouse//8%2:
            raise ValidationError(INVALID_CELL)
        if GameStatus(self.status) is None:
            raise ValidationError('status can not be None')

    class Meta:
        app_label = 'datamodel'
        
    def __str__(self):
        message = (
            '(%d, %s)' % (self.id, self.status) +
            '\tCat [%c] %s(%d, %d, %d, %d)' % (('X' if self.cat_turn else ' '), self.cat_user, self.cat1, self.cat2, self.cat3, self.cat4)
        )

        if self.mouse_user is not None:
            message += ' --- Mouse [%c] %s(%d)' % (('X' if not self.cat_turn else ' '), self.mouse_user, self.mouse)

        return message


class Move(models.Model):
    origin = models.IntegerField(null=False)
    target = models.IntegerField(null=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(null=False)

    def save(self, *args, **kwargs):
        if self.origin < Game.MIN_CELL or self.origin > Game.MAX_CELL:
            return
        if self.target < Game.MIN_CELL or self.target > Game.MAX_CELL:
            return
        if self.origin%2 is not self.origin//8%2:
            return
        if self.target%2 is not self.target//8%2:
            return
        super(Move, self).save(*args, **kwargs)
    
    class Meta:
        app_label = 'datamodel'