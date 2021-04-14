from django.contrib import messages
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render
from django.contrib.auth import login
from boards.models import User
#from boards.tasks import send_email_reg
from .forms import BloggerSignupForm, ReaderSignupForm, AccountForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, CreateView
'''from django.core.mail import send_mail

send_mail('Subject here', 'Here is the message.', 'from@example.com', ['antohagryb@gmail.com'], fail_silently=False)
'''

@receiver(post_save, sender=User)
def specify_user_type(sender, instance=None, created=False, **kwargs):
    if not instance.is_blogger and not instance.is_reader:
        instance.is_reader = True
        instance.save()

'''@receiver(post_save, sender=User)
def specify_user_type(sender, instance=None, created=False, **kwargs):
    if not created:
        send_email_reg(instance)'''


def signup(request):
    return render(request, 'choose_role.html')


class AbstractCertainUserCreateView(CreateView):
    model = User
    template_name = 'signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        res = super().form_valid(form)
        user = User.objects.get(username=form.cleaned_data.get('username'))
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return res


class BloggerCreateView(AbstractCertainUserCreateView):
    form_class = BloggerSignupForm


class ReaderCreateView(AbstractCertainUserCreateView):
    form_class = ReaderSignupForm


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = AccountForm
    template_name = 'my_account.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Account updated successfully')
        return super().form_valid(form)
