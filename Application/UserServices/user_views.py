from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .user_models import UserCartModel, UserCartItemsModel
from .user_serializers import UserCartSerializer, UserCartItemsSerializer

class CartViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserCartSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserCartItemsModel.objects.filter(user_cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, created = UserCartModel.objects.get_or_create(user=self.request.user)
        product = serializer.validated_data['product']
        
        # Check if item already exists in cart
        existing_item = UserCartItemsModel.objects.filter(user_cart=cart, product=product).first()
        
        if existing_item:
            existing_item.quantity += serializer.validated_data.get('quantity', 1)
            existing_item.save()
        else:
            serializer.save(user_cart=cart)

    def create(self, request, *args, **kwargs):
        # Custom create to handle the response correctly if item existed
        cart, created = UserCartModel.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        
        if product_id:
             existing_item = UserCartItemsModel.objects.filter(user_cart=cart, product_id=product_id).first()
             if existing_item:
                 quantity = int(request.data.get('quantity', 1))
                 existing_item.quantity += quantity
                 existing_item.save()
                 serializer = self.get_serializer(existing_item)
                 return Response(serializer.data, status=status.HTTP_200_OK)
        
        return super().create(request, *args, **kwargs)