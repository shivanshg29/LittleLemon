from django.shortcuts import render,HttpResponse
from rest_framework import status,permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from django.contrib.auth.models import User,Group
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *

# Create your views here.

# MENU ITEM VIEWS
@api_view(['GET','POST'])
@permission_classes([permissions.IsAuthenticated])
def MenuItems(request):
    if request.method=='GET':
        menu_items=MenuItem.objects.all()
        serializer=MenuSerializer(menu_items,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    if request.method=='POST':
        if not request.user.groups.filter(name="Manager").exists():
            return Response({'detail':'Unauthorized User'},status=status.HTTP_403_FORBIDDEN)
        
        serializer=MenuSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response({'detail':serializer.errors},status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT','PATCH','DELETE'])
@permission_classes([permissions.IsAuthenticated])
def MenuItemDetail(request,pk):
    menu_item=get_object_or_404(MenuItem, pk=pk)
    if request.method=='GET':
        serializer=MenuSerializer(menu_item)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    if not request.user.groups.filter(name="Manager").exists():
            return Response({'detail':'Unauthorized User'},status=status.HTTP_403_FORBIDDEN)

    if request.method in ['PUT', 'PATCH']:
        serializer = MenuSerializer(menu_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        menu_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# USER GROUP MANAGEMENT
@api_view(['GET','POST'])
@permission_classes([permissions.IsAuthenticated])
def manage_users(request):
    if not request.user.groups.filter(name='Manager').exists():
        return Response({'detail':'Unauthorized'},status=status.HTTP_401_UNAUTHORIZED)
    if request.method=='GET':
        users=User.objects.filter(groups__name="Manager")
        return Response([{'id':user.id,'username':user.username}for user in users])
    if request.method=='POST':
        user_id=request.data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        manager_group, _ = Group.objects.get_or_create(name="Manager")
        user.groups.add(manager_group)
        return Response({'detail': 'User added to Manager group'}, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_manager_user(request, pk):
    if not request.user.groups.filter(name="Manager").exists():
        return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    user = get_object_or_404(User, id=pk)
    manager_group = Group.objects.get(name="Manager")
    user.groups.remove(manager_group)
    return Response({'detail': 'User removed from Manager group'}, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def delivery_crew_users(request):
    if not request.user.groups.filter(name="Manager").exists():
        return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        delivery_crew = User.objects.filter(groups__name="Delivery Crew")
        return Response([{'id': user.id, 'username': user.username} for user in delivery_crew])
    
    if request.method == 'POST':
        user_id = request.data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        delivery_group, _ = Group.objects.get_or_create(name="Delivery Crew")
        user.groups.add(delivery_group)
        return Response({'detail': 'User added to Delivery Crew group'}, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_delivery_crew_user(request, pk):
    if not request.user.groups.filter(name="Manager").exists():
        return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    user = get_object_or_404(User, id=pk)
    delivery_group = Group.objects.get(name="Delivery Crew")
    user.groups.remove(delivery_group)
    return Response({'detail': 'User removed from Delivery Crew group'}, status=status.HTTP_200_OK)
