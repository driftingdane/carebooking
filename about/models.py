from PIL import Image, ExifTags
from django.core.validators import validate_image_file_extension
from django.db import models
from django.utils.html import format_html
from sorl.thumbnail import get_thumbnail


class About(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    info = models.TextField(max_length=1000, blank=True, null=True)
    image = models.ImageField(upload_to="aboutimg/",
                              validators=[validate_image_file_extension],
                              help_text=('Only jpg/jpeg files are allowed'),
                              blank=True, null=True)

    ## Resize and save the image
    def save(self, *args, **kwargs):
        super(About, self).save(*args, **kwargs)
        if self.image:
            imag = Image.open(self.image.path)
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break

                exif = imag.getexif()

                if exif[orientation] == 3:
                    imag = imag.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    imag = imag.rotate(270, expand=True)
                # imag.width, imag.height = imag.height, imag.width
                elif exif[orientation] == 8:
                    imag = imag.rotate(90, expand=True)
            # imag.width, imag.height = imag.height, imag.width

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

    def __str__(self):
        return str(self.id)
