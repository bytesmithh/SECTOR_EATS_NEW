from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    temperature = forms.ChoiceField(
        choices=Feedback.TEMPERATURE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True  # 👈 make sure this is set
    )

    # Override issues to add choices manually
    issues = forms.MultipleChoiceField(
        choices=Feedback.ISSUE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Did you face any issues?"
    )

    class Meta:
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
            'feedback': forms.Textarea(attrs={'rows': 4}),
        }
