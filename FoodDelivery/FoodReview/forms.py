from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        issues = forms.MultipleChoiceField(
        choices=[
            ('late', 'Late Delivery'),
            ('cold', 'Food was cold'),
            ('missing', 'Missing items'),
            ('rude', 'Rude behavior'),
            ('other', 'Other'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Did you face any issues?"
    )
        model = Feedback
        fields = [
            'mood',
            'delivery_speed',
            'etiquette_rating',
            'food_photo',
            'temperature',
            'feedback',
            'issues',
        ]
        widgets = {
            'mood': forms.HiddenInput(),
            'etiquette_rating': forms.HiddenInput(),
            'delivery_speed': forms.NumberInput(attrs={'type': 'range', 'min': 1, 'max': 10}),
            'temperature': forms.RadioSelect(),
            'issues': forms.CheckboxSelectMultiple(),
            'feedback': forms.Textarea(attrs={'rows': 4}),
        }
