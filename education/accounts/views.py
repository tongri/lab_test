from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect
from django.contrib.auth import login
from boards.models import Blogger, User
from .forms import SignUpForm, BloggerSignupForm, ReaderSignupForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, CreateView
import pdb


def signup(request):
    return render(request, 'choose_role.html')


class BloggerCreateView(CreateView):
    model = User
    template_name = 'signup.html'
    form_class = BloggerSignupForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        res = super().form_valid(form)
        user = User.objects.get(username=form.cleaned_data.get('username'))
        login(self.request, user)
        return res


class ReaderCreateView(CreateView):
    model = User
    template_name = 'signup.html'
    form_class = ReaderSignupForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        res = super().form_valid(form)
        user = User.objects.get(username=form.cleaned_data.get('username'))
        login(self.request, user)
        return res


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email', )
    template_name = 'my_account.html'
    success_url = reverse_lazy('my_account')
    success_message = 'Account successfully updated'

    def get_object(self):
        return self.request.user
