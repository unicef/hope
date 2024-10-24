# Generated by Django 3.2.25 on 2024-09-30 09:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0145_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentPlanSupportingDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('payment_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='payment.paymentplan')),
            ],
            options={
                'ordering': ['uploaded_at'],
            },
        ),
    ]
