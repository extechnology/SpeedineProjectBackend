from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action,api_view

from .user_models import UserCartModel, UserCartItemsModel,ContactModel ,UserAddressModel,UserOrderItemsModel,UserOrderModel,OrderStatus
from .user_serializers import UserCartSerializer, UserCartItemsSerializer,ContactUsSerializer,UserSerializer,UserAddressSerializer,OrderItemSerializer,OrderSerializer
from Application.ProductServices.product_models import ProductModel

from rest_framework.views import APIView
from  Application.permissions import IsUserAuthenticated
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.generics import ListAPIView
from django.conf import settings
import razorpay
from django.http import JsonResponse


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


@api_view(['POST'])
def create_order(request):
    user = request.user
    address_id = request.data.get("address_id")  
    order_items = request.data.get("order_items")
    amount = float(request.data.get("amount", 0))

    # Calculate amounts
    total_amount = amount
    discount = 0   # if you apply coupons later
    final_amount = total_amount - discount

    shipping_address = UserAddressModel.objects.get(id=address_id)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    razor_order = client.order.create({
        "amount": int(final_amount * 100),
        "currency": "INR",
        "payment_capture": 1,
    })

    # Create order in DB
    user_order = UserOrderModel.objects.create(
        user=user,
        shipping_address=shipping_address,
        total_amount=total_amount,
        discount_amount=discount,
        final_amount=final_amount,
        razorpay_order_id=razor_order["id"]
    )

    # store ordered items
    for item in order_items:
        UserOrderItemsModel.objects.create(
            user_order=user_order,
            product=ProductModel.objects.get(unique_id=item['product']['unique_id']),
            quantity=item['quantity'],
            price=item['sub_total'],
        )

    return Response({
        "order": razor_order,
        "user_order_id": str(user_order.order_id)
    }, status=200)




@api_view(["POST"])
def verify_payment(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    razorpay_order_id = request.data.get("razorpay_order_id")
    razorpay_payment_id = request.data.get("razorpay_payment_id")
    razorpay_signature = request.data.get("razorpay_signature")

    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return Response({"message": "Missing payment details"}, status=400)

    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        })

        order = UserOrderModel.objects.get(razorpay_order_id=razorpay_order_id)

        order.is_paid = True
        order.status = "confirmed"
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        order.save()

        # Create order status history
        OrderStatus.objects.create(order=order, status="confirmed")

        return Response({"message": "Payment verified successfully"})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


class UserOrderAPIView(APIView):
    permission_classes = [IsUserAuthenticated]

    def get(self, request):
        user = request.user
        orders = UserOrderModel.objects.filter(user=user).order_by('-created')
        serializer = OrderSerializer(orders, many=True,context={'request': request})
        return Response(serializer.data)