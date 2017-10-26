import os
import hashlib
import io

from django.db import models
from django.core import validators
from django.utils import timezone
from django.db.models import deletion
from django.conf import settings
from django.core.files.images import ImageFile


class Product(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)

    title = models.CharField(max_length=80, null=False)
    price = models.FloatField(null=False,
                              validators=[validators.MinValueValidator(0)],
                              help_text='Product price.')
    description = models.TextField(null=False,
                                   help_text='Description, formatted with markdown.')
    is_published = models.BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.updated_at = timezone.now()
        super().save(force_insert, force_update, using, update_fields)

    @property
    def main_image(self):
        if not self.image_set.count():
            return Image.get_or_create_from_path(
                os.path.join(settings.STATIC_ROOT, 'main', 'img', 'no-product-image.png'),
                'no-product-image-placeholder'
            )
        return self.image_set.get(primary_image=True)

    def __str__(self):
        return self.title


def generate_image_name(instance: 'Image', fname):
    name, ext = os.path.splitext(fname)

    h = hashlib.md5()
    h.update(
        fname.encode() +
        str(instance.uploaded_at).encode())

    return h.hexdigest() + ext


def generate_thumb_name(instance):
    name, ext = os.path.splitext(instance.full_image.name)
    return name + '_thumb' + ext


class ImageQuerrySet(models.QuerySet):
    def delete(self):
        for item in self:
            item.delete()
        return super().delete()


class Image(models.Model):
    objects = ImageQuerrySet.as_manager()

    uploaded_at = models.DateTimeField(default=timezone.now, editable=False)
    full_image = models.ImageField(upload_to=generate_image_name,
                                   validators=[validators.FileExtensionValidator(['jpg', 'png'])],
                                   help_text='Choose image to upload.')
    title = models.CharField(max_length=80, null=True, blank=True, unique=True,
                             help_text='(Optional) Image title to show.')

    product = models.ForeignKey(Product, on_delete=deletion.CASCADE, null=True)
    primary_image = models.BooleanField(default=False)
    is_placeholder = models.BooleanField(default=False)

    @property
    def thumb_name(self):
        name, ext = os.path.splitext(self.full_image.name)
        return name + '_thumb' + ext

    @property
    def image_full_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.full_image.name)

    @property
    def thumbnail_full_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.thumb_name)

    def thumb(self):
        name, ext = os.path.splitext(self.full_image.url)
        return name + '_thumb' + ext

    def delete(self, using=None, keep_parents=False):
        print(self.image_full_path)
        if os.path.exists(self.image_full_path):
            print('deleting')
            os.remove(self.image_full_path)

        print(self.thumbnail_full_path)
        if os.path.exists(self.thumbnail_full_path):
            print('deleting')
            os.remove(self.thumbnail_full_path)

        return super().delete(using, keep_parents)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.product and self.is_placeholder:
            # image with product assigned to cant be a placeholder
            raise
        super().save(force_insert, force_update, using, update_fields)
        self.create_thumbnail()

    def create_thumbnail(self):
        if os.path.exists(self.thumbnail_full_path):
            return

        from PIL import Image as PilImage
        from django.core.files.storage import default_storage
        from django.core.files.uploadedfile import SimpleUploadedFile

        with default_storage.open(self.full_image.name) as image_fd:
            image = PilImage.open(image_fd)
            image.thumbnail(settings.THUMBNAIL_SIZE, PilImage.ANTIALIAS)

        thumb_name, thumb_extension = os.path.splitext(self.full_image.name)
        thumb_extension = thumb_extension.lower()

        with io.BytesIO() as tmp:
            image.save(tmp, thumb_extension.replace('.', '').upper())
            tmp.seek(0)

            suf = SimpleUploadedFile(self.full_image.name, tmp.read(), content_type=self.full_image)

        with open(self.thumbnail_full_path, 'wb') as fd:
            fd.write(suf.file.read())

    @classmethod
    def get_or_create_from_path(cls, path, title=None):
        if not Image.objects.filter(title=title).exists():
            image = Image()
            image.title = title
            image.product = None
            image.is_placeholder = True
            image.full_image = ImageFile(open(path, 'rb'))
            image.save()
        else:
            image = Image.objects.get(title=title)

        return image

    def __str__(self):
        return self.title or self.full_image.name
