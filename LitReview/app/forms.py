from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from . import models


class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        for field in ['username', 'password1', 'password2']:
            self.fields[field].help_text = None

    class Meta(UserCreationForm.Meta):
        model = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(max_length=63, label='Nom d’utilisateur')
    password = forms.CharField(max_length=63, widget=forms.PasswordInput, label='Mot de passe')


class TicketForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        fields = ['title', 'description', 'image']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = models.Review
        fields = ['headline', 'rating', 'body']


class FollowForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # récupérer les utilisateurs courant et ceux qui sont déjà suivis
        current_user = kwargs.pop('current_user')
        follows = kwargs.pop('follows')

        super().__init__(*args, **kwargs)

        # filtrer la liste des utilisateurs pour exclure l'utilisateur courant et ceux qui sont déjà suivis
        self.fields['followed_user'].queryset = get_user_model().objects.exclude(id__in=[current_user.id] + follows)

    class Meta:
        model = models.UserFollows
        fields = ['followed_user']
