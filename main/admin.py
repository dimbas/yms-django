from django.contrib import admin

from .models import Image, Product


# Register your models here.

admin.site.register(Product)
admin.site.register(Image)