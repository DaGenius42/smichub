from django.contrib import admin
from .models import Post, News, House, Comments
# Register your models here.
admin.site.register(Post)
admin.site.register(News)
admin.site.register(House)
admin.site.register(Comments)