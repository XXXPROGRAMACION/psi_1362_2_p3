from django import forms
from django.contrib.auth.models import User
from datamodel.models import Move

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password')


class MoveForm(forms.ModelForm):
    origin = forms.IntegerField(initial=0)
    target = forms.IntegerField(initial=0)

    class Meta:
        model = Move
        fields = ('origin', 'target')
