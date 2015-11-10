from django.contrib import admin
from rudeword.models import RudeWord
# Register your models here.

class RudeWordAdmin(admin.ModelAdmin):
    list_display = ['id', 'word']
    readonly_fields = ['id']


admin.site.register(RudeWord, RudeWordAdmin)

