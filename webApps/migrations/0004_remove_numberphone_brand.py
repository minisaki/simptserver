# Generated by Django 4.0.4 on 2022-06-27 13:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webApps', '0003_remove_numberphone_discount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='numberphone',
            name='brand',
        ),
    ]
