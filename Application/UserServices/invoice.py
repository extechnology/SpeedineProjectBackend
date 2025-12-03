

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

# @api_view(['POST'])
def generate_invoice_pdf(request, order_id):
    user = request.user

    order = UserOrderModel.objects.get(order_id=order_id)
    # Don't use .values() - keep as QuerySet of model objects
    order_items = UserOrderItemsModel.objects.filter(user_order=order).select_related('product')
    user_address = UserAddressModel.objects.get(user=user)

    company = {
        'name': 'SpeeDine',
        'address': 'Malappuram, Kerala, India 673633',
        'phone': '+91 99917 07787',
        'email': 'speedine.in@gmail.com',
        'logo_path': r'Application\static\images\Speedine2.png'  # Use raw string
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
            'image': first_image.url if first_image else None,  # Adjust based on your image field
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

