from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def all_products(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'store/products/details.html', {'product': product})


def category_list(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)
    print(products)
    return render(request, 'store/products/category.html', {'category': category, 'products': products})
