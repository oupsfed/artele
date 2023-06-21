# Generated by Django 4.2.2 on 2023-06-21 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_user_telegram_chat_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='telegram_chat_id',
            field=models.IntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
