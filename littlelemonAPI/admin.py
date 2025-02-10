from django.contrib import admin
from .models import Menuitem, Category, Cart, Order, OrderItem, CartItem

# Register your models here.

admin.site.register([Menuitem, Category, Cart, Order, OrderItem,CartItem])
