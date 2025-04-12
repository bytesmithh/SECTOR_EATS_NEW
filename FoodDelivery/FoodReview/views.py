from django.shortcuts import render, redirect
from .forms import FeedbackForm

def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('thank_you')  # Create this URL/view later
    else:
        form = FeedbackForm()
    
    return render(request, 'reviewform.html', {'form': form})


def thank_you(request):
    return render(request, 'thank_you.html')
