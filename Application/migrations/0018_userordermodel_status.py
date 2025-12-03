

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0017_rename_total_price_userorderitemsmodel_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userordermodel',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('shipped', 'Shipped'), ('out_for_delivery', 'Out for Delivery'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
    ]
