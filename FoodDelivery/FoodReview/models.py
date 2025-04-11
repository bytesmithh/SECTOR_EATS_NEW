from django.db import models

class Feedback(models.Model):
    MOOD_CHOICES = (
        (1, 'Very Bad 😡'),
        (2, 'Okay 😐'),
        (3, 'Good 🙂'),
        (4, 'Excellent 🤩'),
    )

    TEMPERATURE_CHOICES = (
        ('hot', 'Hot'),
        ('warm', 'Warm'),
        ('cold', 'Cold'),
    )

    ISSUE_CHOICES = (
        ('late_delivery', 'Late Delivery'),
        ('cold_food', 'Cold Food'),
        ('missing_items', 'Missing Items'),
        ('rude_staff', 'Rude Delivery Staff'),
    )

    mood = models.IntegerField(choices=MOOD_CHOICES)
    delivery_speed = models.IntegerField()
    etiquette_rating = models.IntegerField()
    food_photo = models.ImageField(upload_to='feedback_photos/', null=True, blank=True)
    temperature = models.CharField(max_length=10, choices=TEMPERATURE_CHOICES)
    feedback = models.TextField(blank=True)
    issues = models.JSONField(default=list, blank=True)  # stores list of issues

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback #{self.id} - Mood: {self.mood}"
