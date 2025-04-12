# Generated by Django 5.1.7 on 2025-04-12 08:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodReview', '0002_rename_delivery_person_rating_feedback_delivery_speed_and_more'),
        ('RestaurantApp', '0008_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='order',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='RestaurantApp.order'),
            preserve_default=False,
        ),
    ]
