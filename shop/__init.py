# query_project/shop/__init__.py
# Empty file

# query_project/shop/apps.py
from django.apps import AppConfig

class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'

# query_project/shop/models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "categories"

class Product(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title

# query_project/shop/admin.py
from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'category']
    list_filter = ['category']
    search_fields = ['title']

# query_project/shop/views.py
from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.db import models
from .models import Category

def get_top_categories():
    top_categories = Category.objects.annotate(
        total_price=Coalesce(
            Sum('product__price'), 
            0,
            output_field=models.DecimalField()
        ),
        product_count=Count('product')
    ).filter(
        product_count__gt=0
    ).order_by(
        '-total_price'
    )[:5].values(
        'name',
        'total_price',
        'product_count'
    )

    return [
        {
            'category_name': category['name'],
            'total_price': category['total_price'],
            'product_count': category['product_count']
        }
        for category in top_categories
    ]

def category_list(request):
    categories = get_top_categories()
    return render(request, 'shop/category_list.html', {'categories': categories})