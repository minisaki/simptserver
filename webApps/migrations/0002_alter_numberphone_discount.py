# Generated by Django 4.0.4 on 2022-06-27 07:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webApps', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='numberphone',
            name='discount',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webApps.discount'),
        ),
    ]