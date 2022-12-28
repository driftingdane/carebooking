from PIL.ExifTags import TAGS
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from django.core.validators import validate_image_file_extension
from PIL import Image
from PIL import ExifTags
from sorl.thumbnail import get_thumbnail
from django.utils.html import format_html


class Category(MPTTModel):
    """
    Category Table implimented with MPTT
    """

    name = models.CharField(
        verbose_name=_("Category Name"),
        help_text=_("Required and unique"),
        max_length=255,
        unique=True,
    )

    slug = models.SlugField(verbose_name=_("Category safe url"), max_length=255, unique=True)
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    is_active = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def get_absolute_url(self):
        return reverse('store:category_list', args=[self.slug])

    def __str__(self):
        return self.name


class ProductType(models.Model):
    """
    ProductType Table will provide a list of the
    different types of products that are for sale
    """
    name = models.CharField(verbose_name=_("Product Name"), help_text=_("Required"), max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Product Type")
        verbose_name_plural = _("Product Types")

    def __str__(self):
        return self.name


class ProductSpecification(models.Model):
    """
    The Product Spec Table contains product
    specification on features for the product types
    """
    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)
    name = models.CharField(verbose_name=_("Name"), help_text=_("Required"), max_length=255)

    class Meta:
        verbose_name = _("Product Specification")
        verbose_name_plural = _("Product Specifications")

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    The Product Table contains all product items
    """

    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT)
    title = models.CharField(
        verbose_name=_("Title"),
        help_text=_("Required"),
        max_length=255,
    )
    description = models.TextField(verbose_name=_("description"), help_text=_("Not required"), blank=True)
    slug = models.SlugField(max_length=255)
    regular_price = models.DecimalField(
        verbose_name=_("Regular price"),
        help_text=_("Maximum 999.99"),
        error_messages={
            "name": {
                "max_length": _("The price must be between 0 and 999.99"),
            },
        },
        max_digits=5,
        decimal_places=2,
    )
    discount_price = models.DecimalField(
        verbose_name=_("Discount price"),
        help_text=_("Maximum 999.99"),
        error_messages={
            "name": {
                "max_length": _("The price must be between 0 and 999.99"),
            },
        },
        max_digits=5,
        decimal_places=2,
    )
    is_active = models.BooleanField(
        verbose_name=_("Product visibility"),
        help_text=_("Change product visibility"),
        default=True,
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)


    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def get_absolute_url(self):
        return reverse("store:product_detail", args=[self.slug])

    def __str__(self):
        return self.title


class ProductSpecificationValue(models.Model):
    """
    The Product spec value table holds each of the products individual
    specs or features
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    specification = models.ForeignKey(ProductSpecification, on_delete=models.RESTRICT)
    value = models.CharField(
        verbose_name=_("value"),
        help_text=_("Product specification value (maximum of 255 words"),
        max_length=255,
    )

    class Meta:
        verbose_name = _("Product Specification Value")
        verbose_name_plural = _("Product Specification Values")

    def __str__(self):
        return self.value


class ProductImage(models.Model):
    """
    The Product Image table
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_image")
    image = models.ImageField(
        verbose_name=_("image"),
        upload_to="images/",
        validators=[validate_image_file_extension],
        help_text=('Only jpg/jpeg files are allowed'),
        blank=True, null=True, default="images/default.png"
    )
    alt_text = models.CharField(
        verbose_name=_("Alternative text"),
        help_text=_("Please add alternative text"),
        max_length=255,
        null=True,
        blank=True,
    )
    is_feature = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    ## Resize and save the image
    def save(self, *args, **kwargs):
        # self.image = self.image.lower()
        super(ProductImage, self).save(*args, **kwargs)
        if self.image:
            imag = Image.open(self.image.path)
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break

                exif = imag.getexif()

                exif_table = {}
                for k, v in exif.items():
                    tag = TAGS.get(k)
                    exif_table[tag] = v

                print(exif_table)

                if exif[orientation] == 3:
                    imag.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    imag.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    imag.rotate(90, expand=True)

            except Exception as e:
                print("Exif data spinning errored (might have no exif data)")
                print(e)
                pass

            if imag.width > 800 and imag.height < imag.width:
                output_size = (800, imag.height)
                imag.thumbnail(output_size, Image.ANTIALIAS)

                box = (0, 0, 800, imag.height)
                c_imag = imag.crop(box)
                c_imag.save(self.image.path)

            elif 800 < imag.width < imag.height:
                output_size = (800, imag.height)
                imag.thumbnail(output_size, Image.ANTIALIAS)

                box = (0, 0, 800, imag.height)
                c_imag = imag.crop(box)
                c_imag.save(self.image.path)

            else:
                imag.save(self.image.path)


    @property
    def thumbnail_preview(self):
        if self.image:
            _thumbnail = get_thumbnail(self.image,
                                       '200x150',
                                       upscale=False,
                                       crop=False,
                                       quality=100)
            return format_html(
                '<img src="{}" width="{}" height="{}">'.format(_thumbnail.url, _thumbnail.width, _thumbnail.height))
        # return ""

        else:
            pass

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
