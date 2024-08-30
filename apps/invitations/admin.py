from django.contrib import admin
from .models import MemberInvitation


class MemberInvitationAdmin(admin.ModelAdmin):
    readonly_fields=('pk','landing_url')

admin.site.register(MemberInvitation, MemberInvitationAdmin)
