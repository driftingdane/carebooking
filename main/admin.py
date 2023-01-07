from django.contrib import admin

from main.models import SiteInfo


@admin.register(SiteInfo)
class SiteInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'is_feature', 'image', 'alt_text',)
    prepopulated_fields = {'name': ('alt_text',), }