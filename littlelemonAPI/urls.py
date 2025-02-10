from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

routers = DefaultRouter(trailing_slash=False)

routers.register(r'orders', views.OrderViewSet)
routers.register(r'^cart/menu-items', views.CartItemViewSet)
routers.register(r'order-items', views.OrderItemViewSet)
routers.register(r'categories', views.CategoryViewSet)
routers.register(r'menu-items', views.MenuitemViewSet)
routers.register(r'carts', views.CartViewSet)


urlpatterns =[
    path("api/", include(routers.urls)),
    path("api/groups/manager/users", views.managers, name='managers'),
    path("api/groups/manager/users/<int:id>", views.remove_manager, name='managers_remove'),
    path("api/groups/delivery-crew/users", views.delivery_crew, name='delivery-crew'),
    path("api/groups/delivery-crew/users/<int:id>", views.remove_deliverer, name='delivery-crew_remove'),
]