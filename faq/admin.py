from django.contrib import admin
from models import FaqArticle


class FaqArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['title']


admin.site.register(FaqArticle, FaqArticleAdmin)


