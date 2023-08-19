# Generated by Django 4.2.2 on 2023-08-19 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_user_request_for_access_alter_user_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('USER', 'User'), ('ADMIN', 'Admin'), ('GUEST', 'Guest')], default='GUEST', max_length=16),
        ),
    ]
