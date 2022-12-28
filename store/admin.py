from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe
from mptt.admin import MPTTModelAdmin
from django.contrib.admin.widgets import AdminFileWidget

from .models import (
    Category,
    Product,
    ProductImage,
    ProductSpecification,
    ProductSpecificationValue,
    ProductType,
)

admin.site.register(Category, MPTTModelAdmin)


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [
        ProductSpecificationInline,
    ]


class AdminImageWidget(AdminFileWidget):

    def render(self, name, value, attrs=None, renderer=None):
        output = []

        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)

            output.append(
                f'<a href="{image_url}" target="_blank">'
                f'<img src="{image_url}" alt="{file_name}" width="150" height="150" '
                f'style="object-fit: cover;"/> </a>')

        output.append(super(AdminFileWidget, self).render(name, value, attrs, renderer))
        return mark_safe(u''.join(output))


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    formfield_overrides = {
        models.ImageField: {'widget': AdminImageWidget}
    }


class ProductSpecificationValueInline(admin.TabularInline):
    model = ProductSpecificationValue


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # list_display = ('id', 'type', 'title', 'client', 'url', 'publish', 'thumbnail_preview')
    prepopulated_fields = {'slug': ('title',), }
    inlines = [
        ProductSpecificationValueInline,
        ProductImageInline,
    ]
    #
    # def thumbnail_preview(self, obj):
    #     return obj.thumbnail_preview
    #
    # thumbnail_preview.short_description = 'Thumbnail'
    # thumbnail_preview.allow_tags = True
