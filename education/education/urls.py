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
    url(r'^boards/(?P<pk>\d+)/$', views.board_topics, name="board_topics"),
    url(r'^boards/(?P<pk>\d+)/new/$', views.new_topic, name="new_topic"),
    path('admin/', admin.site.urls),
]
