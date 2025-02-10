from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser,AllowAny
from .models import Menuitem, Category, Cart, Order, OrderItem, CartItem
from .serializers import MenuitemSerializer, CategorySerializer, CartSerializer, OrderSerializer, OrderItemSerializer, CartItemSerializer, UserSerializer, OrderDelivererSerializer
from django.contrib.auth.models import User, Group
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, action
from .permissions import IsManager ,IsDeliveryCrew
from .throttles import RateThrottle



# Create your views here.

class MenuitemViewSet(viewsets.ModelViewSet):
    queryset = Menuitem.objects.all()
    serializer_class = MenuitemSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['price','category', 'feautured']
    search_fields = ['title']
    throttle_classes=[RateThrottle]
    paginate_by = 5
    
    
    def get_permissions(self):
 
        if self.action in ['update','create', 'destroy', 'partial_update']:
            # for other actions (create, destroy ...) only admin can procede them
            
            permission_classes = [IsManager]
        else:
            permission_classes = [AllowAny]
        
        
        return [permissions() for permissions in permission_classes]
    
    
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('user', 'delivery_crew')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']
    search_fields = ['user__username']
    
    def get_permissions(self):
        if self.action in ['destroy']:
            # for other actions (create, destroy ...) only admin can procede them
            permission_classes = [IsManager]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsDeliveryCrew|IsManager] # the manager and the delivery crew can update the order
        else:
            permission_classes = [IsAuthenticated]
        
        return [permissions() for permissions in permission_classes]
    
    def get_serializer_class(self):
        if self.request.user.groups.filter(name = 'Delivery-crew').exists():
            return OrderDelivererSerializer
        else:
            return super().get_serializer_class()
    
    
    def get_queryset(self):
        
        if self.request.user.groups.filter(name = 'Manager').exists():
            return self.queryset.all() # the manager can see all orders
        if self.request.user.groups.filter(name = 'Delivery-crew').exists():
            queryset_deliverer = Order.objects.filter(delivery_crew=self.request.user)# the delivery crew can only see the orders assign to them and can only update the status field
            return queryset_deliverer
        return self.queryset.filter(user = self.request.user) # the user can only see his/her orders
    
    @action(detail = True, methods = ['post'])
    def perform_create(self, serializer):
        
        serializer.save(user = self.request.user) # only the user can create an order
        
        return Response(serializer.data, status = status.HTTP_201_CREATED)
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return self.queryset.filter(user = self.request.user) # only the user can see his/her cart
    
    @action(detail = True, methods = ['post'])
    def perform_create(self, serializer):
        
        serializer.save(user = self.request.user) # only the user can create a cart
        
        return Response(serializer.data, status = status.HTTP_201_CREATED)
    
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(order__user = self.request.user) # only the user can see his/her order items
    
    @action(detail = True, methods = ['post'])
    def perform_create(self, serializer):
        user_order, _ = Order.objects.get_or_create(user=self.request.user)
        serializer.save(order = user_order) # only the user can create an order item
        
        return Response(serializer.data, status = status.HTTP_201_CREATED)
    
class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.prefetch_related('cart', 'menuitem')
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
    
        return self.queryset.filter(cart__user = self.request.user) # only the user can see his/her cart items
    
    @action(detail = True, methods = ['post'])
    def perform_create(self, serializer):

        user_cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart = user_cart) # only the user can create a cart item
        
        return Response(serializer.data, status = status.HTTP_201_CREATED) 
    @action(detail=False, methods=['DELETE'], url_path='delete_all', url_name='delete-all')
    def delete_all(self, request):
        user_cart = get_object_or_404(Cart, user=request.user)# Delete all cart items for the current user's cart
        user_cart.cart_items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    

    


@api_view(['GET', 'POST'])
@permission_classes([IsManager])
def managers(request, pk =  None):
    try:
        group = Group.objects.get(name = 'Manager')
    except Group.DoesNotExist:
        return Response({'message':'Group does not exist'}, status = status.HTTP_404_NOT_FOUND)
    queryset = group.user_set.all()
    serializer= UserSerializer(queryset, many = True)
    if request.method == 'GET':
        return Response(serializer.data)
        
    username = request.data.get('username')
    if username:
        try:
            user = User.objects.get(username = username)
        except User.DoesNotExist:
            return Response({'message':'User does not exist'}, status = status.HTTP_404_NOT_FOUND)
        
        if request.method == 'POST':
            group.user_set.add(user)
            return Response({'message':'user added to the managers'}, status = status.HTTP_201_CREATED)
            
    else:
        return Response('Username is required', status = status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE']) 
@permission_classes([IsManager])
def remove_manager(request, id):
    try:
        user = User.objects.get(pk = id)
    except User.DoesNotExist:
        return Response({'message':'User id does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        group = Group.objects.get(name = 'Manager')
    except Group.DoesNotExist:
        return Response({'message':'Group does not exist'}, status = status.HTTP_404_NOT_FOUND)

    group.user_set.remove(user)
    return Response({'message':'user removed from the Managers '}, status = status.HTTP_204_NO_CONTENT) 

        

@api_view(['GET', 'POST'])
@permission_classes([IsManager])
def delivery_crew(request):
    username = request.data.get('username')
    try:
        group = Group.objects.get(name ='Delivery-crew' )
    except Group.DoesNotExist:
        return Response({'message':'Group does not exist'}, status = status.HTTP_404_NOT_FOUND)

    queryset = group.user_set.all()
    serializer= UserSerializer(queryset, many = True)
    if request.method == 'GET':
        return Response(serializer.data)
        
    if username:
        try:
            user = User.objects.get(username = username)
        except User.DoesNotExist:
            return Response({'message':'User does not exist'}, status = status.HTTP_404_NOT_FOUND)
        
        if request.method == 'POST':
            group.user_set.add(user)
            return Response({'message':'user added to the Delivery Crew'}, status = status.HTTP_201_CREATED)
        
    else:
        return Response('Username is required', status = status.HTTP_400_BAD_REQUEST)
    

    
@api_view(['DELETE']) 
@permission_classes([IsManager])
def remove_deliverer(request, id):

    try:
        user = User.objects.get(pk = id)
    except User.DoesNotExist:
        return Response({'message':'User id does not exist'}, status=status.HTTP_404_NOT_FOUND)
    try:
        group = Group.objects.get(name = 'Delivery-crew')
    except Group.DoesNotExist:
        return Response({'message':'Group does not exist'}, status = status.HTTP_404_NOT_FOUND)
    group.user_set.remove(user)
    return Response({'message':'user removed from the Delivery Crew'}, status = status.HTTP_204_NO_CONTENT)  