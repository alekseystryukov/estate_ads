from django.contrib import admin
from custom_user.admin import EmailUserAdmin
from models import MyCustomEmailUser
from django.utils.translation import ugettext_lazy as _


class MyCustomEmailUserAdmin(EmailUserAdmin):
    """
    You can customize the interface of your model here.
    """
    fieldsets = (
        (None, {'fields': ('email', 'password', 'is_private', 'score', 'phone')}),
        (_('Permissions'), {'fields': ('banned', 'is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

# Register your models here.
admin.site.register(MyCustomEmailUser, MyCustomEmailUserAdmin)