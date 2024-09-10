from django.contrib import admin
from . import models

admin.site.register(models.Project)
admin.site.register(models.Member)
admin.site.register(models.Bot)
admin.site.register(models.Interview)
admin.site.register(models.Question)
admin.site.register(models.Dimension)
admin.site.register(models.ConsentLetter)


class MemberInvitationAdmin(admin.ModelAdmin):
    readonly_fields = ("pk", "landing_url")


admin.site.register(models.MemberInvitation, MemberInvitationAdmin)
