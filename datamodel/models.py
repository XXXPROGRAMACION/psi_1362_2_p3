from django.db import models
from django.contrib.auth.models import User
from enum import Enum


class GameStatus(Enum):
    CREATED = 0
    ACTIVE = 1
    FINISHED = 2


class Game(models.Model):
    cat_user = models.ForeignKey(User, on_delete=models.CASCADE)
    mouse_user = models.ForeignKey(User, on_delete=models.CASCADE)
    cat1 = models.IntegerField(default=0, null=False)
    cat2 = models.IntegerField(default=2, null=False)
    cat3 = models.IntegerField(default=4, null=False)
    cat4 = models.IntegerField(default=6, null=False)
    mouse = models.IntegerField(default=59, null=False)
    cat_turn = models.BooleanField(default=True, null=False)
    status = models.IntegerField(default=GameStatus.CREATED, null=False)

    def save(self, *args, **kwargs):
        if getattr(self, 'cat1') < 0 or getattr(self, 'cat1') > 63:
            return
        if getattr(self, 'cat2') < 0 or getattr(self, 'cat2') > 63:
            return
        if getattr(self, 'cat3') < 0 or getattr(self, 'cat3') > 63:
            return
        if getattr(self, 'cat4') < 0 or getattr(self, 'cat4') > 63:
            return
        if getattr(self, 'mouse') < 0 or getattr(self, 'mouse') > 63:
            return
        if getattr(self, 'cat1') % 2 is not getattr(self, 'cat1')/8 % 2:
            return
        if getattr(self, 'cat2') % 2 is not getattr(self, 'cat2')/8 % 2:
            return
        if getattr(self, 'cat3') % 2 is not getattr(self, 'cat3')/8 % 2:
            return
        if getattr(self, 'cat4') % 2 is not getattr(self, 'cat4')/8 % 2:
            return
        if getattr(self, 'mouse') % 2 is not getattr(self, 'mouse')/8 % 2:
            return
        if GameStatus(self.status) is None:
            return
        super(Game, self).save(*args, **kwargs)


class Move(models.Model):
    origin = models.IntegerField(null=False)
    target = models.IntegerField(null=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(null=False)

    def save(self, *args, **kwargs):
        if getattr(self, 'origin') < 0 or getattr(self, 'origin') > 63:
            return
        if getattr(self, 'target') < 0 or getattr(self, 'target') > 63:
            return
        if getattr(self, 'origin') % 2 is not getattr(self, 'origin')/8 % 2:
            return
        if getattr(self, 'target') % 2 is not getattr(self, 'target')/8 % 2:
            return
        super(Move, self).save(*args, **kwargs)