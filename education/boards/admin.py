from django.contrib import admin
from .models import Board, Topic, Post, Reader, Blogger

# Register your models here.


class BoardAdmin(admin.ModelAdmin):
    fields = ('active', )
    actions = ('make_inactive', )

    def make_inactive(self, request, queryset):
        queryset.update(active=False)


admin.site.register(Board, BoardAdmin)
admin.site.register(Topic)
admin.site.register(Post)
admin.site.register(Reader)
admin.site.register(Blogger)