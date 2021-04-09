from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from accounts import views as account_views
from django.contrib.auth import views as auth_views
from boards import views
from django.conf.urls.static import static
from django.conf import settings 

urlpatterns = [
    url(r'^$', views.BoardListView.as_view(), name="home"),
    path('signup/', account_views.signup, name='signup'),
    path('signup/blogger/', account_views.BloggerCreateView.as_view(), name="signup_blogger"),
    path('signup/reader/', account_views.ReaderCreateView.as_view(), name="signup_reader"),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path('board/create/', views.board_create, name='board_create'),
    path('board/<pk>/update/', views.board_update, name="board_update"),
    path('board/<pk>/delete/<page>/', views.board_delete, name="board_delete"),
    url(r'^boards/(?P<pk>\d+)/$', views.TopicListView.as_view(), name="board_topics"),
    url(r'^boards/(?P<pk>\d+)/new/$', views.new_topic, name="new_topic"),
    path("boards/<pk>/topics/<topic_pk>/", views.PostListView.as_view(), name="topic_posts"),
    path("boards/<pk>/topics/<topic_pk>/reply/", views.reply_topic, name="reply_topic"),
    path("boards/<pk>/topics/<topic_pk>/posts/<post_pk>/edit/", views.PostUpdateView.as_view(), name="edit_post"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name="password_reset"),
    path('reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name="password_reset_confirm"),
    path('reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), name="password_reset_complete"),
    path('settings/password/', auth_views.PasswordChangeView.as_view(template_name="password_change.html"), name="password_change"),
    path('settings/password/done/', auth_views.PasswordChangeDoneView.as_view(template_name="password_change_done.html"), name="password_change_done"),
    path('settings/account/', account_views.UserUpdateView.as_view(), name='my_account'),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
