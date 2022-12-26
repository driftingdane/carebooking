from django.utils import timezone
from sorl.thumbnail import get_thumbnail
from django.utils.html import format_html
from django.core.validators import validate_image_file_extension
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image
from PIL import ExifTags


class Service(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=250, blank=True, null=True, unique=True, allow_unicode=True)
    details = models.TextField(max_length=500)
    created = models.DateTimeField(auto_now=True)
    feat_img = models.ImageField(upload_to="service-img", validators=[validate_image_file_extension],
                                 help_text=('Only jpg/jpeg files are allowed'),
                                 blank=True, null=True)

    class Meta:
        get_latest_by = ['-created', ]
        ordering = ['-id']

    def get_absolute_url(self):
        return reverse('services:service', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(self.title)
        super(Service, self).save(*args, **kwargs)

    def __str__(self):
        return self.id


class Item(models.Model):
    class NewManager(models.Manager):

        def get_queryset(self):
            return super().get_queryset().filter(status='published')

    options = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='items')
    type = models.CharField(max_length=100, null=True, blank=True)
    client = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    info = models.TextField(max_length=500, null=True, blank=True)
    url = models.URLField(max_length=200, null=True, blank=True)
    itemslug = models.SlugField(max_length=250, unique=True, allow_unicode=True)
    publish = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=options, default='published')

    feat_img = models.ImageField(upload_to="item-img/",
                                 validators=[validate_image_file_extension],
                                 help_text=('Only jpg/jpeg files are allowed'),
                                 blank=True, null=True)
    objects = models.Manager()  # default manager
    newmanager = NewManager()  # custom manager

    def get_absolute_url(self):
        return reverse('services:service', args=[self.itemslug])

    ## Resize and save the image
    def save(self, *args, **kwargs):
        if not self.pk:
            self.itemslug = slugify(self.title)
        super(Item, self).save(*args, **kwargs)
        if self.feat_img:
            imag = Image.open(self.feat_img.path)
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
                c_imag.save(self.feat_img.path)

            elif imag.width > 800 and imag.height > imag.width:
                output_size = (800, imag.height)
                imag.thumbnail(output_size, Image.ANTIALIAS)

                box = (0, 0, 800, imag.height)
                c_imag = imag.crop(box)
                c_imag.save(self.feat_img.path)

            else:
                imag.save(self.feat_img.path)

    @property
    def thumbnail_preview(self):
        if self.feat_img:
            _thumbnail = get_thumbnail(self.feat_img,
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
        get_latest_by = ['-publish', ]
        ordering = ('publish',)

    def __str__(self):
        return str(self.id)


class Photo(models.Model):
    item = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='photos')
    title = models.CharField(max_length=200, null=True, blank=True)
    photo = models.ImageField(upload_to='item-img/')

    # resizing the image, you can change parameters like size and quality.
    def save(self, *args, **kwargs):
        super(Photo, self).save(*args, **kwargs)
        img = Image.open(self.photo.path)
        if img.height > 1125 or img.width > 1125:
            img.thumbnail((1125, 1125))
        img.save(self.photo.path, quality=80, optimize=True)
