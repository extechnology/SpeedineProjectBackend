from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action,api_view

from .user_models import (UserCartModel,
    UserCartItemsModel,
    ContactModel ,
    UserAddressModel,
    UserOrderItemsModel,
    UserOrderModel,
    OrderStatus,
    ShippingCharge,
    )
from .user_serializers import (UserCartSerializer,
    UserCartItemsSerializer,
    ContactUsSerializer,
    UserSerializer,
    UserAddressSerializer,
    OrderItemSerializer,
    OrderSerializer,
    ShippingChargeSerializer,
    )
from Application.ProductServices.product_models import ProductModel

from rest_framework.views import APIView
from  Application.permissions import IsUserAuthenticated
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.generics import ListAPIView
from django.conf import settings
from django.core.files.base import ContentFile

from .invoice import generate_invoice_pdf
from .user_emails import order_confirmation_email

import razorpay
from django.core.files.base import ContentFile


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
    
    @action(detail=True, methods=['patch'])
    def update_quantity(self, request, pk=None):
        cart_item = self.get_object()
        quantity = request.data.get("quantity")

        try:
            quantity = int(quantity)
        except:
            return Response({"error": "Invalid quantity"}, status=400)

        if quantity <= 0:
            cart_item.delete()
            return Response({"message": "Item removed"}, status=200)

        cart_item.quantity = quantity
        cart_item.save()

        serializer = self.get_serializer(cart_item)
        return Response(serializer.data, status=200)

    
    
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

    def delete(self, request, pk):
        try:
            address = UserAddressModel.objects.get(pk=pk, user=request.user)
        except UserAddressModel.DoesNotExist:
            return Response({"error": "Address not found"}, status=404)

        address.delete()
        return Response({"success": True}, status=204)

        

@api_view(['POST'])
def create_order(request):
    # Prepare basic data
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    user = request.user
    order_items = request.data.get("order_items", [])

    # Parse and validate amount
    try:
        total_amount = float(request.data.get("amount", 0))
    except (TypeError, ValueError):
        return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

    discount = float(request.data.get("discount", 0)) if request.data.get("discount") is not None else 0.0
    final_amount = max(total_amount - discount, 0.0)

    # Resolve shipping address if provided
    address_id = request.data.get("address_id")
    shipping_address = None
    if address_id:
        try:
            shipping_address = UserAddressModel.objects.get(id=address_id, user=user)
        except UserAddressModel.DoesNotExist:
            return Response({"error": "Shipping address not found"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Create order record in DB
        user_order = UserOrderModel.objects.create(
            user=user,
            shipping_address=shipping_address,
            total_amount=total_amount,
            discount_amount=discount,
            final_amount=final_amount,
        )

        # Create Razorpay order (amount in paise)
        razorpay_order = client.order.create({
            "amount": int(final_amount * 100),
            "currency": "INR",
            "payment_capture": 1,
        })

        user_order.razorpay_order_id = razorpay_order.get("id")
        user_order.save()

        # Store ordered items
        for item in order_items:
            product_info = item.get("product") or {}
            product_uid = product_info.get("unique_id")
            if not product_uid:
                raise ProductModel.DoesNotExist

            product = ProductModel.objects.get(unique_id=product_uid)
            UserOrderItemsModel.objects.create(
                user_order=user_order,
                product=product,
                quantity=item.get("quantity", 1),
                total_amount=item.get("sub_total", 0.0),
                price=product.price,
            )

        return Response({
            "success": True,
            "message": "Order created successfully",
            "order_id": str(user_order.order_id),
            "razorpay_order": razorpay_order
        }, status=status.HTTP_200_OK)

    except ProductModel.DoesNotExist:
        user_order.delete()
        return Response({"error": "Product not found in order items"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # If user_order exists, try to clean up
        try:
            user_order.delete()
        except Exception:
            pass
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def verify_payment(request):
    user = request.user
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

        # Update payment status
        order.is_paid = True
        order.status = "confirmed"
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        order.save()

        # Create order status history
        OrderStatus.objects.create(order=order, status="confirmed")

        # Remove ordered items from user's cart
        order_items = UserOrderItemsModel.objects.filter(user_order=order)
        pdf_response = generate_invoice_pdf(request, order.order_id)
        
        order.invoice.save(
            f"invoice_{order.order_id}.pdf",
            ContentFile(pdf_response.content),  # ✅ FIX
            save=True
        )

        order_confirmation_email(order)
        try:
            user_cart = UserCartModel.objects.get(user=user)
            order_product_ids = order_items.values_list('product_id', flat=True)

            UserCartItemsModel.objects.filter(
                user_cart=user_cart,
                product_id__in=order_product_ids
            ).delete()

        except UserCartModel.DoesNotExist:
            pass  # No cart exists — ignore

        return Response({"status": "success", "message": "Payment verified successfully"}, status=200)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)



class UserOrderAPIView(APIView):
    permission_classes = [IsUserAuthenticated]

    def get(self, request):
        user = request.user
        orders = UserOrderModel.objects.filter(user=user).order_by('-created')
        serializer = OrderSerializer(orders, many=True,context={'request': request})
        return Response(serializer.data)

class ShippingChargeAPIView(APIView):
    permission_classes = [IsUserAuthenticated]

    def get(self, request):
        shipping_charges = ShippingCharge.objects.all().first()
        charge = shipping_charges.charge
        return Response(charge)

class ContactUsAPIView(APIView):

    def post(self, request):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        contacts = ContactModel.objects.all()
        serializer = ContactUsSerializer(contacts, many=True)
        return Response(serializer.data)