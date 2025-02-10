from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsManager(BasePermission):
    
    message = 'You must be a manager to perform this action'
    
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name = 'Manager').exists():
            return True
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name = 'Manager').exists():
            return True
        return False

class IsDeliveryCrew(BasePermission):
    message = 'You must be a delivery crew to perform this action'
    def has_permission(self, request, view):
        
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name = 'Delivery-crew').exists():
            return True
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name = 'Delivery-crew').exists():
            if request.method in SAFE_METHODS:
                return True
            elif obj.delivery_crew == request.user:
                return True
            
            
        return False