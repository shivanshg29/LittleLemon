from rest_framework import permissions

class IsManager(permissions.BasePermission):
    def has_permission(self,request,view):
        return request.user.is_authenticated and request.user.role=='Manager'

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and  request.user.role=='Delivery crew'