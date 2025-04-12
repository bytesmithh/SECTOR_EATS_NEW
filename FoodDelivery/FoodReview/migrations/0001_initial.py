# Generated by Django 5.2 on 2025-04-11 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mood', models.CharField(choices=[('angry', '😡'), ('neutral', '😐'), ('happy', '😊'), ('excited', '🤣')], max_length=10)),
                ('speed', models.IntegerField()),
                ('delivery_person_rating', models.IntegerField()),
                ('food_photo', models.ImageField(blank=True, null=True, upload_to='food_photos/')),
                ('temperature', models.CharField(choices=[('hot', 'Hot'), ('warm', 'Warm'), ('cold', 'Cold')], max_length=10)),
                ('feedback', models.TextField(blank=True)),
                ('issues', models.CharField(blank=True, max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
