from django.contrib import messages
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render
from django.contrib.auth import login
from boards.models import User
from .decorators import check_recaptcha
from .forms import BloggerSignupForm, ReaderSignupForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, CreateView
from django.contrib.auth import views as auth_views


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
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = User.objects.get(username=form.cleaned_data.get('username'))
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        return super().post(request=self.request, *args, **kwargs)


class BloggerCreateView(AbstractCertainUserCreateView):
    form_class = BloggerSignupForm


class ReaderCreateView(AbstractCertainUserCreateView):
    form_class = ReaderSignupForm


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email', )
    template_name = 'my_account.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user

    '''def get_form(self, form_class=None):
        form_class = BloggerSignupForm if self.request.user.is_blogger else ReaderSignupForm
        return super().get_form(form_class=form_class)'''

    def form_valid(self, form):
        messages.success(self.request, 'Account updated successfully')
        return super().form_valid(form)
