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
    amount = request.data.get("amount")
    order_items = request.data.get("order_items", [])
    address_id = request.data.get("address_id")

    try:
        # Step 1: Create Order in Django
        user_order = UserOrderModel.objects.create(
            user=user,
            shipping_address_id=address_id,
            total_amount=amount,
            discount_amount=0.0,   # if any coupon logic later
            final_amount=amount,   # initial same as total
        )

        # Step 2: Create Razorpay Order
        razorpay_order = client.order.create({
            "amount": float(amount) * 100,  # Razorpay takes paise
            "currency": "INR",
            "payment_capture": 1
        })

        user_order.razorpay_order_id = razorpay_order["id"]
        user_order.save()

        # Step 3: Save Order Item Records
        for item in order_items:
            UserOrderItemsModel.objects.create(
                user_order=user_order,
                product=ProductModel.objects.get(unique_id=item["product"]["unique_id"]),
                quantity=item["quantity"],
                price=item["sub_total"]    # storing snapshot price
            )

        # Step 4: Response back to frontend
        return Response({
            "success": True,
            "message": "Order created successfully",
            "order_id": user_order.order_id,
            "razorpay_order": razorpay_order
        }, status=status.HTTP_200_OK)

    except ProductModel.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_400_BAD_REQUEST)
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

        order_items = UserOrderItemsModel.objects.filter(user_order=order)
        
        user_cart = UserCartModel.objects.get(user=user)
        
        cart_items = UserCartItemsModel.objects.filter(user_cart=user_cart)
        
        order_product_ids = order_items.values_list('product_id', flat=True)
        
        UserCartItemsModel.objects.filter(
            user_cart=user_cart,
            product_id__in=order_product_ids
        ).delete()
        
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












# views.py
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from io import BytesIO
from datetime import datetime, timedelta

def generate_invoice_pdf(request):
    # Sample data
    company = {
        'name': 'Tech Solutions Inc.',
        'address': '123 Business Street, Suite 100\nNew York, NY 10001',
        'phone': '+1 (555) 123-4567',
        'email': 'contact@techsolutions.com',
        'logo_path': 'path/to/logo.png'  # Optional: set to None if no logo
    }
    
    customer = {
        'name': 'Acme Corporation',
        'address': '456 Client Avenue\nLos Angeles, CA 90001',
        'phone': '+1 (555) 987-6543',
        'email': 'billing@acmecorp.com'
    }
    
    invoice_info = {
        'invoice_number': 'INV-2024-001',
        'date': datetime.now().strftime('%B %d, %Y'),
        'due_date': (datetime.now() + timedelta(days=30)).strftime('%B %d, %Y'),
        'notes': 'Thank you for your business! Payment is due within 30 days.'
    }
    
    # Invoice items
    items = [
        {'description': 'Web Development Services', 'quantity': 40, 'unit_price': 150.00},
        {'description': 'UI/UX Design', 'quantity': 20, 'unit_price': 120.00},
        {'description': 'SEO Optimization', 'quantity': 10, 'unit_price': 100.00},
        {'description': 'Hosting & Maintenance', 'quantity': 1, 'unit_price': 500.00},
    ]
    
    # Calculate totals
    subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
    tax_rate = 0.08  # 8% tax
    tax = subtotal * tax_rate
    total = subtotal + tax
    
    # Create buffer
    buffer = BytesIO()
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    right_align = ParagraphStyle(
        'RightAlign',
        parent=styles['Normal'],
        alignment=TA_RIGHT,
    )
    
    # Add logo if exists (optional)
    # Uncomment and provide valid path if you have a logo
    try:
        logo = Image('Application\static\images\Speedine2.png', width=2*inch, height=1*inch)
        logo.hAlign = 'LEFT'
        elements.append(logo)
        elements.append(Spacer(1, 0.3*inch))
    except:
        pass
    
    # Company info and Invoice title in table
    header_data = [
        [
            Paragraph(f"<b><font size=14>{company['name']}</font></b><br/>{company['address']}<br/>{company['phone']}<br/>{company['email']}", styles['Normal']),
            Paragraph(f"<b><font size=18 color='#2C3E50'>INVOICE</font></b><br/><br/><b>Invoice #:</b> {invoice_info['invoice_number']}<br/><b>Date:</b> {invoice_info['date']}<br/><b>Due Date:</b> {invoice_info['due_date']}", right_align)
        ]
    ]
    
    header_table = Table(header_data, colWidths=[3.5*inch, 3*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Customer info
    elements.append(Paragraph("<b><font size=12>BILL TO:</font></b>", styles['Normal']))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(f"<b>{customer['name']}</b><br/>{customer['address']}<br/>{customer['phone']}<br/>{customer['email']}", styles['Normal']))
    elements.append(Spacer(1, 0.4*inch))
    
    # Invoice items table
    items_data = [['Description', 'Quantity', 'Unit Price', 'Total']]
    
    for item in items:
        item_total = item['quantity'] * item['unit_price']
        items_data.append([
            item['description'],
            str(item['quantity']),
            f"${item['unit_price']:.2f}",
            f"${item_total:.2f}"
        ])
    
    # Add totals
    items_data.append(['', '', '', ''])
    items_data.append(['', '', 'Subtotal:', f"${subtotal:.2f}"])
    items_data.append(['', '', f'Tax ({int(tax_rate*100)}%):', f"${tax:.2f}"])
    items_data.append(['', '', 'TOTAL:', f"${total:.2f}"])
    
    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (-1, -5), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -5), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -5), [colors.white, colors.HexColor('#ECF0F1')]),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        
        # Total section
        ('FONTNAME', (2, -3), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (2, -3), (-1, -3), 1, colors.black),
        ('LINEABOVE', (2, -1), (-1, -1), 2, colors.black),
        ('BACKGROUND', (2, -1), (-1, -1), colors.HexColor('#E8F6F3')),
        ('FONTSIZE', (2, -1), (-1, -1), 12),
    ]))
    
    elements.append(items_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Notes
    if invoice_info['notes']:
        elements.append(Paragraph("<b>Notes:</b>", styles['Heading4']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(invoice_info['notes'], styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer = Paragraph(
        "<i>This is a computer-generated invoice. No signature required.</i>",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1)
    )
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF value
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_info["invoice_number"]}.pdf"'
    response.write(pdf)
    
    return response

