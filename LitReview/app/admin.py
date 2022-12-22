from django.contrib import admin
from app.models import *


class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'time_created')


class UserFollowsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'followed_user')


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Review)
admin.site.register(UserFollows, UserFollowsAdmin)
