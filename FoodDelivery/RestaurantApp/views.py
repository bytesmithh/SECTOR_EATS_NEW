
from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
import re
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login,authenticate
from django.contrib.auth.hashers import make_password
<<<<<<< HEAD

from .models import Profile,Restaurant
from .forms import RestaurantForm
=======
from .models import Profile  

>>>>>>> e4752600748491bea43bc30cea3f181777c090a6

# Create your views here.
def home_view(request):
    return render(request,"index.html")

def is_valid_password(password):
    return len(password) >= 8 and re.search(r'[^A-Za-z0-9]', password)

def signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        role=request.POST.get('role')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup_view')

        if not is_valid_password(password1):
            messages.error(request, "Password must be at least 8 characters long and contain at least one special character.")
            return redirect('signup_view')

        if User.objects.filter(username=name).exists():
            messages.error(request, "Username already taken.")
            return redirect('signup_view')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('signup_view')

        user = User.objects.create(
            username=name,
            email=email,
            password=make_password(password1)
        )

        # Save extra details in Profile (linked via OneToOneField to User)
        Profile.objects.create(
            user=user,
            phone=phone,
            address=address,
            city=city,
            role=role
        )

        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login_view')

    return render(request, "signup.html")





def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        print("Login attempt with:", email, password)

        try:
            user_obj = User.objects.get(email=email)
            print("User found:", user_obj.username)
        except User.DoesNotExist:
            print("User not found")
            messages.error(request, "Invalid email or password.")
            return redirect('login_view')

        user = authenticate(request, username=user_obj.username, password=password)
        print("Authenticated user:", user)

        if user is not None:
            login(request, user)
            profile = Profile.objects.get(user=user)

            messages.success(request, f"Welcome, {user.username}!")

            if profile.role == 'restaurant_admin':
                return redirect('home_view')
            else:
                return redirect('user_dashboard_view')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login_view')

    return render(request, 'login.html')



def about_us_view(request):
    return render(request,"about_us.html")



#logic for Ai model integration

HUGGINGFACE_API_KEY = "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"  

@csrf_exempt
def ai_chat(request):
    if request.method == 'POST':
        user_input = request.POST.get('message', '')

        allowed_keywords = ['order', 'menu', 'food', 'delivery', 'track', 'cancel', 'status', 'item']
        if not any(word in user_input for word in allowed_keywords):
            return JsonResponse({
                'reply': '❌ I can only help with food orders, menus, or delivery queries. Please keep your questions related.'
            })



        if not user_input:
            return JsonResponse({"reply": "Please enter a message."})

        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
        }

        prompt = f"[INST] {user_input} [/INST]"

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7,
                "return_full_text": False
            }
        }

        response = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
            headers=headers,
            json=payload
        )

        result = response.json()
        print(result)

        try:
            reply = result[0]["generated_text"]
        except Exception as e:
            reply = "Sorry! Something went wrong or the model needs a better prompt."

        return JsonResponse({"reply": reply})
    
def chatbot_page(request):
    return render(request, "chatbot.html")

def user_dashboard_view(request):
    return render(request,"user_dashboard.html")




def admin_dashboard(request):
    return render(request,'admin_dashboard.html')


def add_restaurant(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            
            messages.success(request, 'Restaurant added successfully!')
            return redirect('admin_dashboard')  
    else:
        form = RestaurantForm()

    return render(request, 'add_restaurant.html', {'form': form})
def list_restaurants(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'list_restaurants.html', {'restaurants': restaurants})



def delete_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if request.method == 'POST':
        restaurant.delete()
        messages.success(request, f'Restaurant "{restaurant.name}" deleted successfully.')
        return redirect('admin_dashboard')
    return render(request, 'confirm_delete.html', {'restaurant': restaurant})

def edit_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, "Restaurant updated successfully!")
            return redirect('list_restaurants')
    else:
        form = RestaurantForm(instance=restaurant)
    return render(request, 'edit_restaurant.html', {'form': form})


