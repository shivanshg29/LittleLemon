from django.shortcuts import render,HttpResponse
from rest_framework import status,permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from django.contrib.auth.models import User,Group
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
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
    
# USER GROUP MANAGEMENT VIEWS

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

# CART MANAGEMENT VIEWS
@api_view(['GET','POST','DELETE'])
@permission_classes([permissions.IsAuthenticated])
def cart_items(request):
    if request.method=='GET':
        items = Cart.objects.filter(user=request.user)
        serializer=CartSerializer(items,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    if request.method=='POST':
        menu_item_id = request.data.get('menuitem_id')
        quantity = request.data.get('quantity', 1)
        menu_item = get_object_or_404(MenuItem, id=menu_item_id)
        unit_price = menu_item.price
        total_price = unit_price * int(quantity)
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            menuitem=menu_item,
            defaults={'quantity': quantity, 'unit_price': unit_price, 'price': total_price}
        )
        # Increase the quantity
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.price = cart_item.quantity * cart_item.unit_price
            cart_item.save()
        
        return Response({'detail': 'Item added to cart'}, status=status.HTTP_201_CREATED)
    
    if request.method == 'DELETE':
        Cart.objects.filter(user=request.user).delete()
        return Response({'detail': 'Cart cleared'}, status=status.HTTP_204_NO_CONTENT)

# ORDER MANAGEMENT ENPOINTS
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def orders(request):
    user = request.user
    
    if request.method == 'GET':
        if user.groups.filter(name='Manager').exists():
            orders = Order.objects.all()
        elif user.groups.filter(name='Delivery Crew').exists():
            orders = Order.objects.filter(delivery_crew=user)
        else:
            orders = Order.objects.filter(user=user)
        
        data = []
        for order in orders:
            items = OrderItem.objects.filter(order=order)
            order_data = model_to_dict(order)
            order_data['items'] = [model_to_dict(item) for item in items]
            data.append(order_data)
        
        return Response({'orders': data}, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        order = Order.objects.create(user=user, total=sum(item.price for item in cart_items))
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=cart_item.price
            )
        cart_items.delete()
        return Response({'message': 'Order created successfully', 'order_id': order.id}, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def order_details(request, orderId):
    user = request.user
    order = get_object_or_404(Order, id=orderId)
    
    if request.method == 'GET':
        if user != order.user and not user.groups.filter(name='Manager').exists():
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        items = OrderItem.objects.filter(order=order)
        order_data = model_to_dict(order)
        order_data['items'] = [model_to_dict(item) for item in items]
        return Response(order_data, status=status.HTTP_200_OK)
    
    elif request.method in ['PUT', 'PATCH']:
        if not user.groups.filter(name='Manager').exists() and not user.groups.filter(name='Delivery Crew').exists():
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        if 'delivery_crew' in data and user.groups.filter(name='Manager').exists():
            order.delivery_crew = get_object_or_404(User, id=data['delivery_crew'])
        if 'status' in data:
            order.status = data['status']
        order.save()
        return Response({'message': 'Order updated successfully'}, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        if not user.groups.filter(name='Manager').exists():
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        order.delete()
        return Response({'message': 'Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
