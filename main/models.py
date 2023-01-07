from PIL import Image, ExifTags, ImageOps
from PIL.ExifTags import TAGS
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_image_file_extension
from django.db import models


class SiteInfo(models.Model):
    name = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True, null=True)
    image = models.ImageField(
        verbose_name=_("header"),
        upload_to="header/",
        validators=[validate_image_file_extension],
        help_text=('Only jpg/jpeg files are allowed'),
        blank=True, null=True, default="header/default.png")

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
        super(SiteInfo, self).save(*args, **kwargs)
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

            if imag.width > 1500 and imag.height < imag.width:
                box = (0, 1920, 0, 600)  # left, top, right, bottom
                c_imag = ImageOps.crop(imag, box)
                output_size = (1920, 600)
                c_imag.thumbnail(output_size, Image.ANTIALIAS)
                c_imag.save(self.image.path, quality=90)

            elif 1500 < imag.width < imag.height:
                box = (0, 1920, 0, 600)  # left, top, right, bottom
                c_imag = ImageOps.crop(imag, box)
                output_size = (1920, 600)
                c_imag.thumbnail(output_size, Image.ANTIALIAS)
                c_imag.save(self.image.path, quality=90)

            else:
                imag.save(self.image.path)

    class Meta:
        verbose_name = _("Site info")
