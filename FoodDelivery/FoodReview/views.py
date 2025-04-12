from django.shortcuts import render, redirect
from .forms import FeedbackForm

from django.shortcuts import get_object_or_404
from RestaurantApp.models import Order

def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)

        if form.is_valid():
            feedback = form.save(commit=False)

            # ✅ Get order ID from query params
            order_id = request.GET.get('order_id')

            # ✅ Fetch and assign the order
            order = get_object_or_404(Order, id=order_id)
            feedback.order = order

            feedback.save()
            return redirect('thank_you')  # or some success page
    else:
        form = FeedbackForm()

    return render(request, 'reviewform.html', {'form': form})


def thank_you(request):
    return render(request, 'thank_you.html')
