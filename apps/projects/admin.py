from django.contrib import admin
from . import models

admin.site.register(models.Project)
admin.site.register(models.Member)
admin.site.register(models.Bot)
admin.site.register(models.Interview)
admin.site.register(models.Question)
admin.site.register(models.Dimension)
admin.site.register(models.ConsentLetter)
admin.site.register(models.Case)
admin.site.register(models.CaseAttribute)
admin.site.register(models.Record)
admin.site.register(models.AIModel)
admin.site.register(models.Query)


class MemberInvitationAdmin(admin.ModelAdmin):
    readonly_fields = ("pk", "landing_url")


admin.site.register(models.MemberInvitation, MemberInvitationAdmin)
