from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length = 255, db_index = True)  
    
    def __str__(self):
        return self.title


class Menuitem(models.Model):
    title = models.CharField(max_length = 255, db_index = True)
    price = models.DecimalField(max_digits = 6, decimal_places = 2)
    feautured = models.BooleanField(db_index = True, default = False)
    category = models.ForeignKey(Category, on_delete = models.PROTECT)
    
    def __str__(self):
        return self.title  
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    
    def __str__(self):
        return self.user.username + ' ' + str(self.items.count())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE, related_name = 'items') # many-to-one with cart
    menuitem = models.ForeignKey(Menuitem, on_delete = models.CASCADE) # one-to-many with menuitem
    quantity = models.SmallIntegerField(default = 1)
    unit_price = models.DecimalField(max_digits = 6, decimal_places = 2) # can be access via menuitem.price
    price = models.DecimalField(max_digits = 6, decimal_places = 2) # can be replaced with a @property method
    
    class Meta:
        unique_together = ('cart', 'menuitem') # Each inner tupple specifies a set of fields that must be unique when considered together.
    
    def __str__(self):
        return self.menuitem.title + ' ' + str(self.quantity)
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete = models.SET_NULL, related_name = 'delivery_crew', null = True, blank = True)
    status = models.BooleanField(db_index = True, default = False)
    # choises =[('Pending','Pending'),('Out for Delivery','Out for Delivery'),('Delivered','Delivered')]
    # status = models.CharField(max_length = 255, db_index = True,choises = choises, default = 'Pending')
    total = models.DecimalField(max_digits = 6, decimal_places = 2)
    date = models.DateTimeField(db_index = True, auto_now_add = True)
    
    def __str__(self):
        return f'Order {self.id}'
    
    class Meta:
        ordering = ['-date']
    
    
    
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name= 'order_items',on_delete = models.CASCADE)
    menuitem = models.ForeignKey(Menuitem, on_delete = models.CASCADE)
    quantity = models.SmallIntegerField(default = 1)
    unit_price = models.DecimalField(max_digits = 6, decimal_places = 2)
    price = models.DecimalField(max_digits = 6, decimal_places = 2)
    
    class Meta:
        unique_together = ('order', 'menuitem')
        ordering = ['order']
        
    def __str__(self):
        return self.menuitem.title + ' ' + str(self.quantity)   
    
   





