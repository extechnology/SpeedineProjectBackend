from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .user_models import UserCartModel, UserCartItemsModel,ContactModel ,UserAddressModel,UserOrderItemsModel,UserOrderModel,OrderStatus
from .user_serializers import UserCartSerializer, UserCartItemsSerializer,ContactUsSerializer,UserSerializer,UserAddressSerializer,OrderItemSerializer,OrderSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from  Application.permissions import IsUserAuthenticated
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.generics import ListAPIView



class CartViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserCartSerializer
    permission_classes = [IsUserAuthenticated]

    def get_queryset(self):
        return UserCartModel.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        cart, created = UserCartModel.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)


    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = UserCartModel.objects.get(user=request.user)
        cart.usercartitemsmodel_set.all().delete()
        return Response({'status': 'Cart cleared'}, status=status.HTTP_200_OK)



class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = UserCartItemsSerializer
    permission_classes = [IsUserAuthenticated]

    def get_queryset(self):
        return UserCartItemsModel.objects.filter(user_cart__user=self.request.user)


    def perform_create(self, serializer):
        cart, created = UserCartModel.objects.get_or_create(user=self.request.user)
        product = serializer.validated_data['product']
        
        existing_item = UserCartItemsModel.objects.filter(user_cart=cart, product=product).first()
        
        if existing_item:
            existing_item.quantity += serializer.validated_data.get('quantity', 1)
            existing_item.save()
        else:
            serializer.save(user_cart=cart)

    def create(self, request, *args, **kwargs):
        cart, created = UserCartModel.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        
        if product_id:
             existing_item = UserCartItemsModel.objects.filter(user_cart=cart,product__unique_id=product_id).first()

             if existing_item:
                 quantity = int(request.data.get('quantity', 1))
                 existing_item.quantity += quantity
                 existing_item.save()
                 serializer = self.get_serializer(existing_item)
                 return Response(serializer.data, status=status.HTTP_200_OK)
        
        return super().create(request, *args, **kwargs)
    
    
class ContactUsViewSet(viewsets.ModelViewSet):
    queryset = ContactModel.objects.all()
    serializer_class = ContactUsSerializer
    
    
class CurrentUserAPIView(APIView):
    permission_classes = [IsUserAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

class UserAddressAPIView(APIView):
    permission_classes = [IsUserAuthenticated]

    def get(self, request):
        addresses = UserAddressModel.objects.filter(user=request.user).order_by('-is_default', '-created')
        serializer = UserAddressSerializer(addresses, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = UserAddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk):
        try:
            address = UserAddressModel.objects.get(pk=pk, user=request.user)
        except UserAddressModel.DoesNotExist:
            return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)
    
        if request.data.get("is_default") is True:
            UserAddressModel.objects.filter(user=request.user).update(is_default=False)
    
        serializer = UserAddressSerializer(address, data=request.data, partial=True)
    
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class CheckoutAPIView(APIView):
    permission_classes = [IsUserAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        data = request.data

        shipping_address_id = data.get("shipping_address")
        cart_items = data.get("items")

        if not cart_items:
            return Response({"message": "Cart is empty"}, status=400)

        order = UserOrderModel.objects.create(
            user=user,
            shipping_address_id=shipping_address_id
        )

        total = 0

        for item in cart_items:
            product = item["product"]
            quantity = item["quantity"]
            price = item["price"]

            total += price * quantity

            UserOrderItemsModel.objects.create(
                user_order=order,
                product_id=product,
                quantity=quantity,
                price=price,
            )

        order.total_amount = total
        order.final_amount = total 
        order.save()

        OrderStatus.objects.create(order=order, status="pending", is_active=True)

        return Response(OrderSerializer(order).data, status=201)


class OrderListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return UserOrderModel.objects.filter(user=self.request.user).order_by("-created")
    

class UpdateOrderStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = UserOrderModel.objects.filter(order_id=order_id).first()
        if not order:
            return Response({"message": "Order not found"}, status=404)

        status_name = request.data.get("status")
        OrderStatus.objects.create(order=order, status=status_name, is_active=True)

        return Response({"message": "Status updated"})
