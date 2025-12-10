

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
from rest_framework.decorators import api_view
from django.http import FileResponse

from django.conf import settings
import os

from .user_models import UserOrderModel, UserOrderItemsModel, UserAddressModel

from django.views.decorators.csrf import csrf_exempt

logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'Speedine2.png')

from .ui_models import CompnayLogo


logo = CompnayLogo.objects.first()

@csrf_exempt
def generate_invoice_pdf(request, order_id):
    user = request.user

    order = UserOrderModel.objects.get(order_id=order_id)
    # Don't use .values() - keep as QuerySet of model objects
    order_items = UserOrderItemsModel.objects.filter(user_order=order).select_related('product')
    user_address = order.shipping_address

    company = {
        'name': 'SpeeDine',
        'address': 'Malappuram, Kerala, India 673633',
        'phone': '+91 99917 07787',
        'email': 'speedine.in@gmail.com',
        'logo_path': logo.image.url
    }

    customer = {
        'name': user_address.name,
        'address': user_address.address,
        'phone': user_address.phone,
        'email': user.email
    }
    
    invoice_info = {
        'invoice_number': 'INV-2024-001',
        'date': datetime.now().strftime('%B %d, %Y'),
        'due_date': (datetime.now() + timedelta(days=30)).strftime('%B %d, %Y'),
        'notes': 'Thank you for your purchase.'
    }

    items = []
    total = 0

    for item in order_items:
        # Access the related product object
        product = item.product  # Assuming ForeignKey field name is 'product'
        
        # Get the first image - images is a RelatedManager, not a list
        first_image = product.images.first()  # or product.images.all()[0] if you prefer
        
        items.append({
            'description': product.name,  # Get product name
            'quantity': item.quantity,
            'unit_price': item.price,
            'image': first_image,
        })
        total += item.quantity * item.price

    # Calculate totals
    subtotal = total
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
    
    # Add logo if exists (use raw string or forward slashes)
    try:
        logo = Image(r'Application\static\images\Speedine2.png', width=2*inch, height=1*inch)
        logo.hAlign = 'LEFT'
        elements.append(logo)
        elements.append(Spacer(1, 0.3*inch))
    except:
        pass
    
    # ... rest of your PDF generation code remains the same ...
    
    # Company info and Invoice title in table
        # HEADER SECTION (Company + Invoice details)
    header_data = [
        [
            Paragraph(
                f"<b><font size=16>{company['name'].upper()}</font></b><br/>"
                f"{company['address']}<br/>"
                f"Phone: {company['phone']}<br/>"
                f"Email: {company['email']}",
                styles['Normal']
            ),
            Paragraph(
                f"<b><font size=14>TAX INVOICE</font></b><br/><br/>"
                f"<b>Invoice No :</b> {invoice_info['invoice_number']}<br/>"
                f"<b>Invoice Date :</b> {invoice_info['date']}<br/>",
                right_align
            )
        ]
    ]

    header_table = Table(header_data, colWidths=[4*inch, 3*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.2*inch))

    # BUYER DETAILS SECTION
    buyer_table = Table([
        [
            Paragraph("<b>Buyer details</b><br/>"
                      f"{customer['name']}<br/>{customer['address']}<br/>"
                      f"Phone: {customer['phone']}<br/>Email: {customer['email']}",
                      styles['Normal']),
            Paragraph("<b>Order & despatch details</b><br/>"
                      f"GST No : 32AKXPN6398M1Z1<br/>"
                      f"FSSAI : 11324010000725",
                      styles['Normal'])
        ]
    ], colWidths=[4*inch, 3*inch])

    buyer_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.6, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F2F3F4')),
    ]))
    elements.append(buyer_table)
    elements.append(Spacer(1, 0.3*inch))

    # ITEM TABLE
    items_data = [[
        'S/n', 'Item', 'HSN', 'Unit', 'Qty', 'Rate', 'Value',
        'Tax%', 'CGST', 'SGST', 'Total'
    ]]

    sn = 1
    for item in items:
        item_total = item['quantity'] * item['unit_price']
        cgst = (item_total * tax_rate) / 2
        sgst = (item_total * tax_rate) / 2

        items_data.append([
            sn, item['description'], '9109100', 'NOS', str(item['quantity']),
            f"{item['unit_price']:.2f}", f"{item_total:.2f}",
            f"{int(tax_rate*100)}%", 'Included', 'Included',
            f"{item_total}"
        ])
        sn += 1

    # Add totals
    items_data.append(['', '', '', '', '', '', f"{subtotal:.2f}", '', f"{tax/2:.2f}", f"{tax/2:.2f}", f"{total:.2f}"])

    items_table = Table(items_data, repeatRows=1)
    items_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.8, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#D6EAF8')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.3*inch))

    # Amount in words
    elements.append(Paragraph(f"<b>Amount in words:</b> Six Hundred Seventy Four", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))

    # Bank + Declaration + Signature line
    footer_table = Table([
        [
            Paragraph("<b>Bank details</b><br/>SBI KONDOTTY<br/>A/C No: 43418161591<br/>IFSC: SBIN0070311", styles['Normal']),
            Paragraph("<b>DECLARATION:</b><br/>We declare that this invoice shows the actual price and particulars are true.", styles['Normal']),
            Paragraph("<b>Authorized Signatory</b><br/><br/><br/><i>_________________</i>", right_align),
        ]
    ], colWidths=[2.5*inch, 3*inch, 1.5*inch])

    footer_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(footer_table)
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("This is a computer generated invoice", right_align))

    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf    

