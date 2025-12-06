from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def order_confirmation_email(order):
    subject = f"Order Confirmed - #{order.order_id}"
    to_email = [order.user.email]  # should be list
    from_email = settings.EMAIL_HOST_USER

    text_content = f"Your order #{order.order_id} has been confirmed. Total Amount: ₹{order.final_amount}"

    # HTML Template
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h2 style="color: #007bff; text-align: center;">Order Confirmation</h2>

                <p style="font-size: 16px; color: #333;">
                    Hi <b>{order.user.username}</b>,<br><br>
                    Thank you for your purchase from <b>Speedine</b> 🎉 <br>
                    Your order has been successfully confirmed!
                </p>

                <p style="font-size: 15px; color: #333;">
                    <b>Order ID:</b> {order.order_id} <br>
                    <b>Total Amount:</b> ₹{order.final_amount} <br>
                    <b>Payment Status:</b> Successful
                </p>

                <p style="font-size: 14px; color: #555;">
                    Your invoice has been attached to this email. You can download or print it anytime.
                </p>

                <div style="text-align: center; margin-top: 25px;">
                    <span style="font-size: 16px; font-weight: bold; color: #007bff;">
                        Thank you for shopping with us 🚀
                    </span>
                </div>

                <p style="font-size: 12px; color: #aaa; text-align: center; margin-top: 30px;">
                    &copy; 2025 Speedine
                </p>
            </div>
        </body>
    </html>
    """

    # Email Setup
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")

    # Attach Invoice PDF (assuming binary file already stored in order.invoice_pdf)
    if order.invoice_pdf:
        msg.attach(
            filename=f"Invoice_{order.order_id}.pdf",
            content=order.invoice_pdf.read(),  # Read binary PDF data
            mimetype="application/pdf"
        )

    msg.send()