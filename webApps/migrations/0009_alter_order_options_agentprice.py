# Generated by Django 4.0.5 on 2022-08-02 02:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webApps', '0008_numberphone_discount_numberphone_is_priority'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-update_at']},
        ),
        migrations.CreateModel(
            name='AgentPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, default='', null=True, unique=True)),
                ('rate_discount', models.FloatField(default=0)),
                ('create', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('profile', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='webApps.profile')),
            ],
        ),
    ]