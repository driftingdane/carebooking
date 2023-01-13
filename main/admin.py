from django.contrib import admin

from main.models import SiteInfo


@admin.register(SiteInfo)
class SiteInfoAdmin(admin.ModelAdmin):
  list_display = [field.name for field in SiteInfo._meta.get_fields()]
  prepopulated_fields = {'name': ('alt_text',), }
