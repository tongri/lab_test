from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from boards.models import Category, Blogger, User, Reader


class MyDateInput(forms.DateInput):
    input_type = 'date'


class LoginForm(AuthenticationForm):

    def is_valid(self):
        res = super().is_valid()
        if not self.data.get('g-recaptcha-response'):
            self.add_error(None, 'Please enter correct captcha')
            return False
        return res


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'categories')

    def is_valid(self):
        res = super().is_valid()
        if not self.data.get('g-recaptcha-response'):
            self.add_error(None, 'Please enter correct captcha')
            return False
        return res


class BloggerSignupForm(SignUpForm):
    country = forms.CharField(max_length=50)
    birthday = forms.DateField(widget=MyDateInput)

    class Meta(SignUpForm.Meta):
        pass

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_blogger = True
        user.save()
        Blogger.objects.create(user=user, birthday=self.cleaned_data.get('birthday'),
                               country=self.cleaned_data.get('country'))
        return user


class ReaderSignupForm(SignUpForm):
    is_eighteen = forms.BooleanField(required=True)

    class Meta(SignUpForm.Meta):
        pass

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_reader = True
        user.save()
        Reader.objects.create(user=user, is_eighteen=self.cleaned_data.get('is_eighteen'))
        return user
