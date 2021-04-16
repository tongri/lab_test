from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.files import File
from PIL import Image
from boards.models import Category, Blogger, User, Reader
import re
import math


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
        required=False
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'categories')
        required = ('username', 'email', 'password1', 'password2')

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
    is_eighteen = forms.BooleanField(required=False)

    class Meta(SignUpForm.Meta):
        pass

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_reader = True
        user.save()
        Reader.objects.create(user=user, is_eighteen=self.cleaned_data.get('is_eighteen'))
        return user


class AccountForm(forms.ModelForm):
    transform = forms.CharField(widget=forms.HiddenInput(), required=False)
    width = forms.CharField(widget=forms.HiddenInput(), required=False)
    height = forms.CharField(widget=forms.HiddenInput(), required=False)
    resized_width = forms.CharField(widget=forms.HiddenInput(), required=False)
    resized_height = forms.CharField(widget=forms.HiddenInput(), required=False)
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'id': 'fileUplaod', 'name': 'image', 'class': 'image'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'avatar', 'transform', 'width', 'height')
        #widgets = {'avatar': forms.FileInput(attrs={'id': 'fileUplaod', 'name': 'image', 'class': 'image'})}


    def save(self, commit=True):
        account = super().save()
        resized_width = self.cleaned_data.get('resized_width').rstrip("px")
        resized_height = self.cleaned_data.get('resized_height').rstrip("px")
        if not self.cleaned_data.get('avatar') or not resized_width:
            return account
        resized_width, resized_height = int(resized_width), int(resized_height)
        width = self.cleaned_data.get('width').rstrip("px")
        height = self.cleaned_data.get('height').rstrip("px")
        transform = self.cleaned_data.get('transform')
        dot = re.findall(r'\d+\.\d+', transform)
        x = dot[0] if "translateX" in transform else 0 #check for optional params in form
        y = 0 if "translateY" not in transform else dot[0] if not x else dot[1]
        x, y, width, height = list(map(lambda tmp: math.floor(float(tmp)), (x, y, width, height)))
        image = Image.open(account.avatar)
        resized_image = image.resize((resized_width, resized_height), Image.ANTIALIAS)
        cropped_image = resized_image.crop((x, y, x+width, y+height))
        cropped_image.save(account.avatar.path)
        return account
