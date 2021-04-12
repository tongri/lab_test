from django.contrib import admin
from .models import Board, Topic, Post, Reader, Blogger

# Register your models here.

admin.site.register(Board)
admin.site.register(Topic)
admin.site.register(Post)
admin.site.register(Reader)
admin.site.register(Blogger)