# Generated by Django 5.1.7 on 2025-04-11 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodReview', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feedback',
            old_name='delivery_person_rating',
            new_name='delivery_speed',
        ),
        migrations.RenameField(
            model_name='feedback',
            old_name='speed',
            new_name='etiquette_rating',
        ),
        migrations.RenameField(
            model_name='feedback',
            old_name='created_at',
            new_name='submitted_at',
        ),
        migrations.AlterField(
            model_name='feedback',
            name='food_photo',
            field=models.ImageField(blank=True, null=True, upload_to='feedback_photos/'),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='issues',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='mood',
            field=models.IntegerField(choices=[(1, 'Very Bad 😡'), (2, 'Okay 😐'), (3, 'Good 🙂'), (4, 'Excellent 🤩')]),
        ),
    ]
