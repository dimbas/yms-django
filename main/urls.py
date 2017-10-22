from django.conf.urls import url

from .views import products, product

urlpatterns = [
    url(r'^$', products),
    url(r'^(?P<product_id>[0-9]*)', product, name='detail')
]
