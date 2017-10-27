from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Product


# Create your views here.
def products(request: HttpRequest):
    all_products = Product.objects.filter(is_published=True).order_by('pk').all()
    paginator = Paginator(all_products, settings.ITEMS_PER_PAGE)

    page_index = request.GET.get('page')
    try:
        page = paginator.page(page_index)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return render(request, 'products.html', {'products': page})


def product(request: HttpRequest, product_id):
    prod = Product.objects.get(pk=product_id)

    placeholder = prod.main_image

    return render(request, 'product.html',
                  {'product': prod,
                   'images': prod.image_set.order_by('pk').all(),
                   'placeholder': placeholder})
