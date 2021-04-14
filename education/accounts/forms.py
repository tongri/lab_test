from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.files import File
from PIL import Image
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
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'avatar', 'x', 'y', 'width', 'height')

    def save(self, commit=True):
        photo = super().save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')

        image = Image.open(photo.file)
        cropped_image = image.crop((x, y, w+x, h+y))
        resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
        resized_image.save(photo.file.path)

        return photo
