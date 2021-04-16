from django import forms
from .models import Topic, Post, Board, Image, User


class MyDateInput(forms.DateInput):
    input_type = 'date'


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        exclude = 'active',



class NewTopicForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'Whats on your mind?'}
        ),
        max_length=4000,
        help_text='Max length is 4000'
    )
    file_field = forms.FileField(widget=forms.FileInput(attrs={'multiple': True,
                                                               'onchange': 'readURL(this);',
                                                               'accept': ".jpg, .jpeg, .png",
                                                               }), required=False)

    class Meta:
        model = Topic
        exclude = ('views', 'board', 'starter')


class PhotoForm(forms.ModelForm):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = Image
        fields = ('file_field', )


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('message', )
