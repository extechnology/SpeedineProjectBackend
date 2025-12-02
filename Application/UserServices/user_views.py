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
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    user = request.user
    user_order, created = UserOrderModel.objects.get_or_create(user=user) 
    currency = "INR"
    amount = request.data.get('amount')
    order_items = request.data.get('order_items')
    try:
        if currency is None:
            currency = "INR"

        order_data = {
            "amount": float(amount) * 100,  # Convert to paise
            "currency": currency, 
            "payment_capture": 1,  # Auto-capture payment
        }
    
        order = client.order.create(data=order_data)
        user_order.razorpay_order_id = order['id']
        user_order.save()

        for item in order_items:
            UserOrderItemsModel.objects.create(
                user_order=user_order,
                product=ProductModel.objects.get(unique_id=item['product']['unique_id']),
                quantity=item['quantity'],
                price=item['sub_total'],
            )

        return Response({"order": order,"user_order":user_order}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(["POST"])
def verify_payment(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    user = request.user
    payment_response = request.data.get("response", {})

    # Extract data from request
    razorpay_order_id = payment_response.get("razorpay_order_id")
    razorpay_payment_id = payment_response.get("razorpay_payment_id")
    razorpay_signature = payment_response.get("razorpay_signature")
    
    # Check for missing parameters
    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return JsonResponse({"status": "error", "message": "Missing required fields"}, status=400)

    try:
        # Verify the payment signature
        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        })

        # Fetch the corresponding order
        try:
            order = UserOrderModel.objects.get(razorpay_order_id=razorpay_order_id)
        except UserOrderModel.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Order not found"}, status=404)
    
        order.is_paid = True
        order.status = "confirmed"
        order.save()
    
        return JsonResponse({"status": "success", "message": "Payment verified successfully"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)



class UserOrderAPIView(APIView):
    permission_classes = [IsUserAuthenticated]

    def get(self, request):
        user = request.user
        orders = UserOrderModel.objects.filter(user=user).order_by('-created')
        serializer = OrderSerializer(orders, many=True,context={'request': request})
        return Response(serializer.data)