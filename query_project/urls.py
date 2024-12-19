from django.contrib import admin
from django.urls import path
from shop.views import category_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', category_list, name='category_list'),
]