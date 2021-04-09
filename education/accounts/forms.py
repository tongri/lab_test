from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from boards.models import Category, Blogger


class MyDateInput(forms.DateInput):
    input_type = 'date'


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'categories')


class BloggerSignupForm(SignUpForm):
    country = forms.CharField(max_length=50)
    birthday = MyDateInput()

    class Meta(SignUpForm.Meta):
        pass

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_blogger = True
        user.save()
        Blogger.objects.create(user=user, birthday=self.cleaned_data.get('birthday'),
                               country=self.cleaned_data.get('country'))
        return user
