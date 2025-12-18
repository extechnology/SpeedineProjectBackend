from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from io import BytesIO
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt

from Application.Authentication.auth_utils import get_user_from_request
from .user_models import UserOrderModel, UserOrderItemsModel

@csrf_exempt
def generate_invoice_pdf(request, order_id):
    # -------------------- AUTH --------------------
    user = get_user_from_request(request)

    # -------------------- ORDER DATA --------------------
    order = UserOrderModel.objects.get(order_id=order_id)
    order_items = UserOrderItemsModel.objects.filter(
        user_order=order
    ).select_related('product')

    user_address = order.shipping_address


    # -------------------- COMPANY --------------------
    company = {
        'name': 'SpeeDine',
        'address': 'Malappuram, Kerala, India 673633',
        'phone': '+91 99917 07787',
        'email': 'speedine.in@gmail.com',
        'logo_path': 'Application/static/images/Speedine2.png'
    }

    customer = {
        'name': user_address.name,
        'address': f'{user_address.address}, {user_address.city}, {user_address.state}, {user_address.country}, {user_address.pincode}',
        'phone': user_address.phone,
        'email': user.email,
    }

    invoice_info = {
        'invoice_number': f'INV-{order.id}',
        'date': datetime.now().strftime('%d %b %Y'),
        'due_date': (datetime.now() + timedelta(days=30)).strftime('%d %b %Y'),
    }

    # -------------------- ITEMS --------------------
    items = []
    subtotal = 0


    for item in order_items:
        product = item.product
        unit_price = item.product.price
        line_total = item.total_amount
        subtotal += line_total

        items.append({
            'name': product.name,
            'qty': item.quantity,
            'rate': unit_price,
            'total': line_total
        })

    # -------------------- PDF BUFFER --------------------
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )

    elements = []
    styles = getSampleStyleSheet()

    right_align = ParagraphStyle(
        'RightAlign',
        parent=styles['Normal'],
        alignment=TA_RIGHT
    )

    # -------------------- LOGO --------------------
    try:
        logo = Image(company['logo_path'], 2 * inch, 1 * inch)
        elements.append(logo)
        elements.append(Spacer(1, 0.3 * inch))
    except Exception:
        pass

    # -------------------- HEADER --------------------
    header_table = Table([
        [
            Paragraph(
                f"<b><font size='16'>{company['name']}</font></b><br/>"
                f"{company['address']}<br/>"
                f"Phone: {company['phone']}<br/>"
                f"Email: {company['email']}",
                styles['Normal']
            ),
            Paragraph(
                f"<b><font size='14'>TAX INVOICE</font></b><br/><br/>"
                f"Invoice No: {invoice_info['invoice_number']}<br/>"
                f"Date: {invoice_info['date']}",
                right_align
            )
        ]
    ], colWidths=[4 * inch, 3 * inch])

    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 0.3 * inch))

    # -------------------- BUYER DETAILS --------------------
    buyer_table = Table([
        [
            Paragraph(
                f"<b>Buyer Details</b><br/>"
                f"{customer['name']}<br/>"
                f"{customer['address']}<br/>"
                f"Phone: {customer['phone']}<br/>"
                f"Email: {customer['email']}",
                styles['Normal']
            ),
            Paragraph(
                "<b>Order Details</b><br/>"
                "GST: 32AKXPN6398M1Z1<br/>"
                "FSSAI: 11324010000725",
                styles['Normal']
            )
        ]
    ], colWidths=[4 * inch, 3 * inch])

    buyer_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F4F6F7'))
    ]))

    elements.append(buyer_table)
    elements.append(Spacer(1, 0.3 * inch))

    # -------------------- ITEM TABLE --------------------
    table_data = [[
        'S/N', 'Item', 'Qty', 'Rate', 'Tax', 'Total'
    ]]

    for i, item in enumerate(items, start=1):
        table_data.append([
            i,
            item['name'],
            item['qty'],
            f"{item['rate']:.2f}",
            'Included',
            f"{item['total']:.2f}"
        ])
    
    if order.shipping_charge > 0:
        table_data.append([
            '', '', '', 'Shipping Charge', '', f"{order.shipping_charge:.2f}"
        ])

    table_data.append(['', '', '', 'Grand Total', '', f"{subtotal:.2f}"])

    items_table = Table(
        table_data,
        colWidths=[0.6 * inch, 2.6 * inch, 0.8 * inch, 1.2 * inch, 1.2 * inch, 1.4 * inch]
    )

    items_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.7, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D6EAF8')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
    ]))

    elements.append(items_table)
    elements.append(Spacer(1, 0.3 * inch))

    # -------------------- FOOTER --------------------
    elements.append(Paragraph(
        "<b>Declaration:</b> Tax included in product price. No separate tax charged.",
        styles['Normal']
    ))

    elements.append(Spacer(1, 0.4 * inch))
    elements.append(Paragraph("Authorized Signatory", right_align))

    # -------------------- BUILD PDF --------------------
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="invoice_{order.order_id}.pdf"'
    response.write(pdf)

    return response
