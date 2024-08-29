from django.contrib import admin
from .models import Project, Membership

admin.site.register(Project)

class MembershipAdmin(admin.ModelAdmin):
    readonly_fields=('invitation_code','invitation_landing_url')

admin.site.register(Membership, MembershipAdmin)
