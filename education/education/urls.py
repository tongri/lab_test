from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from accounts import views as account_views
from django.contrib.auth import views as auth_views
from boards import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^signup/$', account_views.signup, name="signup"),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    url(r'^boards/(?P<pk>\d+)/$', views.board_topics, name="board_topics"),
    url(r'^boards/(?P<pk>\d+)/new/$', views.new_topic, name="new_topic"),
    url(r'^reset/$', auth_views.PasswordResetView.as_view(
        template_name='password_reset.html',
        email_template_name='password_reset_email.html',
        subject_template_name='password_reset_subject.txt'
        ), name='password_reset'),
    url(r'^reset/done/$', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
        name='password_reset_confirm'),
    url(r'^reset/complete/$', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'),
        name='password_reset_complete'),
    path('admin/', admin.site.urls),
]