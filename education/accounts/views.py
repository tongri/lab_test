from django.contrib import messages
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render
from django.contrib.auth import login
from boards.models import Blogger, User
from .forms import SignUpForm, BloggerSignupForm, ReaderSignupForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, CreateView
import pdb


@receiver(post_save, sender=User)
def specify_user_type(sender, instance=None, created=False, **kwargs):
    if not instance.is_blogger and not instance.is_reader:
        instance.is_reader = True
        instance.save()


def signup(request):
    return render(request, 'choose_role.html')


class AbstractCertainUserCreateView(CreateView):
    model = User
    template_name = 'signup.html'
    success_url = reverse_lazy('lazy')

    def form_valid(self, form):
        res = super().form_valid(form)
        user = User.objects.get(username=form.cleaned_data.get('username'))
        login(self.request, user)
        return res


class BloggerCreateView(AbstractCertainUserCreateView):
    form_class = BloggerSignupForm


class ReaderCreateView(AbstractCertainUserCreateView):
    form_class = ReaderSignupForm


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email', )
    template_name = 'my_account.html'
    success_url = reverse_lazy('my_account')

    def get_object(self, queryset=None):
        return self.request.user

    '''def get_form(self, form_class=None):
        form_class = BloggerSignupForm if self.request.user.is_blogger else ReaderSignupForm
        return super().get_form(form_class=form_class)'''

    def form_valid(self, form):
        messages.success(self.request, 'Account updated successfully')
        return super().form_valid(form)
