from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect
from django.contrib.auth import login
from boards.models import Blogger
from .forms import SignUpForm, BloggerSignupForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, CreateView


class BloggerCreateView(CreateView):
    model = Blogger
    template_name = 'signup.html'
    form_class = BloggerSignupForm

    def form_valid(self, form):
        res = super().form_valid(form)
        login()
        return res

@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email', )
    template_name = 'my_account.html'
    success_url = reverse_lazy('my_account')

    def get_object(self):
        return self.request.user
