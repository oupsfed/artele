# Generated by Django 4.2.2 on 2023-06-29 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0004_alter_cart_amount_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('IP', 'in_progress'), ('D', 'done'), ('C', 'cancelled')], default='in_progress', max_length=256),
        ),
    ]
