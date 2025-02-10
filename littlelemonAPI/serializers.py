from . import models
from rest_framework import serializers 
from django.contrib.auth.models import User, Group

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']
               
class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'groups']
        
class UserOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
             
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'
        
class MenuitemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only = True)
    category = CategorySerializer(read_only=True)
    class Meta:
        model = models.Menuitem
        fields = ['id', 'title', 'price', 'feautured', 'category_id', 'category']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = '__all__'
        
        
class CartItemSerializer(serializers.ModelSerializer):
    cart = CartSerializer(read_only=True)
    menuitem= MenuitemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = models.CartItem
        fields = ['id', 'cart', 'menuitem', 'quantity', 'unit_price', 'price', 'menuitem_id']

class OrderItemSerializer(serializers.ModelSerializer):
    # menuitem = serializers.PrimaryKeyRelatedField(queryset=models.Menuitem.objects.all())
    class Meta:
        model = models.OrderItem
        fields =[ 'id', 'order', 'menuitem', 'quantity', 'unit_price']
       
 
   
class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    user= UserOrderSerializer(read_only=True)
    class Meta:
        model = models.Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'order_items']
        read_only_fields = ['user', 'date']
        
class OrderDelivererSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    user= UserOrderSerializer(read_only=True)
    class Meta:
        model = models.Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'order_items']
        read_only_fields = ['id', 'user', 'delivery_crew', 'order_items', 'date']  
        


        
        
