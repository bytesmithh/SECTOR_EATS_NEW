
from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
import re
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
from .decorators import admin_required,user_required
from FoodReview.models import Feedback
import random
from django.core.mail import send_mail
from .forms import MenuItemForm
from .models import Profile,Restaurant,MenuItem,Cart, Order, OrderItem
from .forms import RestaurantForm

FLASK_BASE = "http://127.0.0.1:5000/api"

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
            role='customer' 
        )

        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login_view')

    return render(request, "signup.html")





import requests
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Profile, User

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect('login_view')

        user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            login(request, user)
            profile = Profile.objects.get(user=user)

            # Sync user to Flask
            user_payload = {
                "id": user.id,
                "name": user.first_name or f"User {user.id}",
                "email": user.email,
                "address": profile.address,
                "city": profile.city,
                "mobile": profile.phone,
                "role": profile.role,
                "password": "default"  
            }

            try:
                flask_response = requests.post(f"{FLASK_BASE}/create_user", json=user_payload)
                print("Flask Sync Response:", flask_response.status_code, flask_response.text)
            except requests.exceptions.RequestException as e:
                print("Error sending user to Flask:", str(e))

            messages.success(request, f"Welcome, {user.username}!")

            if profile.role == 'restaurant_admin':
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard_view')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login_view')

    return render(request, 'login.html')




def about_us_view(request):
    return render(request,"about_us.html")

def logout_view(request):
    logout(request)
    return redirect('login_view')  




HUGGINGFACE_API_KEY = "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"  




@csrf_exempt
def ai_chat(request):
    if request.method == 'POST':
        user_input = request.POST.get('message', '')

        allowed_keywords = ['order', 'menu', 'food', 'delivery', 'track', 'cancel', 'status', 'item','burger','pizza','sandwich']
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

@login_required
@user_required
def user_dashboard_view(request):
    user_profile = request.user.profile
    user_city = user_profile.city.lower()

    restaurants = Restaurant.objects.filter(
        is_approved=True,
        location__icontains=user_city
    )

    return render(request, "user_dashboard.html", {'restaurants': restaurants})





@admin_required
@login_required
def admin_dashboard(request):
    return render(request,'admin_dashboard.html')

@admin_required
@login_required
def add_restaurant(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES)
        print("Form Submitted")

        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.admin = request.user
            restaurant.save()
            messages.success(request, 'Restaurant added successfully!')
            return redirect('admin_dashboard')
        else:
            print("Form errors:", form.errors)
    else:
        form = RestaurantForm()

    return render(request, 'add_restaurant.html', {'form': form})



@admin_required
@login_required
def list_restaurants(request):
    restaurants = Restaurant.objects.filter(admin=request.user)
    return render(request, 'list_restaurants.html', {'restaurants': restaurants})



@admin_required
@login_required
def delete_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if request.method == 'POST':
        restaurant.delete()
        messages.success(request, f'Restaurant "{restaurant.name}" deleted successfully.')
        return redirect('admin_dashboard')
    return render(request, 'confirm_delete.html', {'restaurant': restaurant})

@admin_required
@login_required
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


@admin_required
@login_required
def add_menu_item(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.restaurant = restaurant
            menu_item.save()
            messages.success(request, 'Menu item added successfully!')
            return redirect('list_restaurants')
    else:
        form = MenuItemForm()
    
    menu_items = MenuItem.objects.filter(restaurant=restaurant)
    return render(request, 'add_menu_item.html', {
      'form': form,
      'restaurant': restaurant,
      'menu_items': menu_items
     })



@login_required
def restaurant_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, delivery_available=True)
    menu_items = MenuItem.objects.filter(restaurant=restaurant)
    return render(request, 'restaurant_menu.html', {'restaurant': restaurant, 'menu_items': menu_items})


@admin_required
@login_required
def edit_menu_item_view(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('add_menu_item', restaurant_id=item.restaurant.id)
    else:
        form = MenuItemForm(instance=item)
    return render(request, 'edit_menu_item.html', {'form': form, 'item': item})

@admin_required
@login_required
def delete_menu_item_view(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    restaurant_id = item.restaurant.id
    item.delete()
    return redirect('add_menu_item', restaurant_id=restaurant_id)




@login_required
@user_required  
def user_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'user_profile.html', {'profile': profile})



@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    try:
        qty = int(request.GET.get('qty', 1))
        if qty < 1:
            qty = 1
    except ValueError:
        qty = 1

    cart_item, created = Cart.objects.get_or_create(user=request.user, item=item)
    
    if created:
        cart_item.quantity = qty
    else:
        cart_item.quantity += qty

    cart_item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'message': f'Added {qty} item(s) to cart'})
    
    return redirect('view_cart')



@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'view_cart.html', {'cart_items': cart_items, 'total': total})



@login_required
@require_POST
def empty_cart(request):
    Cart.objects.filter(user=request.user).delete()
    return redirect('view_cart')

@csrf_exempt
@login_required
def update_quantity_ajax(request, item_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_item = get_object_or_404(Cart, user=request.user, item_id=item_id)
        data = json.loads(request.body)
        change = data.get('change', 0)
        cart_item.quantity = max(1, cart_item.quantity + int(change))
        cart_item.save()
        return JsonResponse({'success': True, 'new_quantity': cart_item.quantity})
    return JsonResponse({'success': False}, status=400)

@login_required
def checkout_view(request):
    user = request.user

    cart_items = Cart.objects.filter(user=user)
    total = sum(item.total_price() for item in cart_items)
    customer = {
        'name': user.get_full_name(),
        'email': user.email,
        'phone': user.profile.phone,
        'address': user.profile.address,
        'city': user.profile.city,
    }

    context = {
        'customer': customer,
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'checkout.html', context)



@require_POST
@login_required
def place_order(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')

    total = sum(item.total_price() for item in cart_items)

    order = Order.objects.create(
        user=user,
        total_amount=total,
        address=user.profile.address,
        city=user.profile.city,
        phone=user.profile.phone
    )

    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            item=cart_item.item,
            quantity=cart_item.quantity,
            price=cart_item.item.price
        )

    cart_items.delete()
    messages.success(request, "Order placed successfully!")
    return redirect('user_dashboard_view') 

def admin_recent_orders(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        order = Order.objects.get(id=order_id)
        order.status = new_status
        order.save()

    orders = Order.objects.select_related('user').prefetch_related('items__item').order_by('-created_at')
    active_orders = orders.exclude(status__in=["Delivered", "Rejected"])
    delivered_orders = orders.filter(status="Delivered")  
    rejected_orders = orders.filter(status="Rejected")
    context = {
        'active_orders': active_orders,
        'delivered_orders': delivered_orders,
        'rejected_orders': rejected_orders
    }
    
    return render(request, 'admin_recent_orders.html', context)


@login_required
@user_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__item').order_by('-created_at')
    return render(request, 'user_orders.html', {'orders': orders})



def admin_feedback(request):
    feedbacks = Feedback.objects.all().order_by('-submitted_at')  
    return render(request, 'admin_feedback.html', {'feedbacks': feedbacks})

def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'order_detail.html', {'order': order})


def check_phone(request):
    phone = request.GET.get('phone')
    if phone:

        user_exists = Profile.objects.filter(phone=phone).exists()
        return JsonResponse({'exists': user_exists})
    return JsonResponse({'exists': False})


def phone_login_view(request):
    if request.method == "POST":
        data = json.loads(request.body) 
        phone = data.get('phone')
        password = data.get('password')

        try:
            profile = Profile.objects.get(phone=phone)
            user = profile.user 
            authenticated_user = authenticate(request, username=user.username, password=password)

            if authenticated_user:
                login(request, authenticated_user)
                return JsonResponse({"success": True, "redirect_url": '/'})
            else:
                return JsonResponse({"success": False, "message": "Invalid password."})
        except Profile.DoesNotExist:
            return JsonResponse({"success": False, "message": "Phone number not registered."})
    return JsonResponse({"success": False, "message": "Invalid request."})



FLASK_BASE = "http://127.0.0.1:5000/api"

LOGIN_URL = f"{FLASK_BASE}/login"
RESTAURANTS_URL = f"{FLASK_BASE}/restaurants"
MENU_URL = lambda rid: f"{FLASK_BASE}/menu-items/restaurant/{rid}"


def fetch_token(email, password):
    response = requests.post(LOGIN_URL, json={"email": email, "password": password})
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

@login_required
@user_required
def api_restaurant_view(request):

    #currently hard code but i will change this later
    token = fetch_token("john@example.com", "securepassword123")  
    if not token:
        return render(request, "error.html", {"message": "Authentication failed"})

    headers = {"Authorization": f"Bearer {token}"}
    restaurants_response = requests.get(RESTAURANTS_URL, headers=headers)

    print("Restaurants Response:", restaurants_response.json())
    if restaurants_response.status_code != 200:
        return render(request, "error.html", {"message": "Failed to fetch restaurants"})


    restaurants_data = restaurants_response.json()
    
    print("Fetched Restaurants Data:", restaurants_data)  

    for restaurant in restaurants_data:
        rid = restaurant["id"]
        menu_response = requests.get(MENU_URL(rid), headers=headers)


        print(f"Menu Response for restaurant {restaurant['name']} (ID: {rid}):", menu_response.json())  

        if menu_response.status_code == 200:
            menu_data = menu_response.json()
            restaurant["menu_items"] = menu_data  
        else:
            print(f"Failed to fetch menu for restaurant {restaurant['name']}")
            restaurant["menu_items"] = []

    return render(request, "other_restaurants.html", {
        "restaurants": restaurants_data
    })



def error_view(request):
    error_message = "An error occurred, please try again later."
    return render(request, 'error.html', {'error_message': error_message})

ORDER_URL = f"{FLASK_BASE}/order"



@csrf_exempt
def place_order_api(request):
    if request.method == 'POST':
        try:
            user = request.user
            user_id = user.id
            print(f"Logged-in user ID: {user_id}")

            try:
                data = json.loads(request.body)
                print(f"Data received in request: {data}")
            except json.JSONDecodeError as e:
                return JsonResponse({'message': 'Invalid JSON'}, status=400)

            try:
                user_profile = Profile.objects.get(user_id=user_id)
            except Profile.DoesNotExist:
                return JsonResponse({'message': 'Profile not found for user'}, status=400)

            # Prepare the payload for Flask
            payload = {
                "user_id": user_id,
                "restaurant_id": data.get("restaurant_id"),
                "items": data.get("items", []),
                "total_price": data.get("total_price"),
                "city": user_profile.city,
                "address": user_profile.address,
            }

            if not payload["restaurant_id"] or not payload["items"] or not payload["total_price"]:
                return JsonResponse({'message': 'Missing required fields'}, status=400)
            
            flask_api_url = f"{FLASK_BASE}/order"
            response = requests.post(flask_api_url, json=payload, headers={"Content-Type": "application/json"})

            print(f"Flask response: {response.status_code} - {response.text}")

            if response.status_code == 201:
                return JsonResponse({'message': 'Order placed successfully!'}, status=201)
            else:
                return JsonResponse({'message': 'Flask error', 'details': response.text}, status=400)

        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'message': f'Internal server error: {str(e)}'}, status=500)

    return JsonResponse({'message': 'Invalid request method'}, status=405)

@admin_required
@login_required
def contact_messages(request):
    try:
        response = requests.get(f"{FLASK_BASE}/contact")  
        response.raise_for_status()
    
        contacts = response.json()
        
        if not isinstance(contacts, list):
            raise ValueError("Expected a list of contacts from the API.")
        
        for contact in contacts:
            if not all(key in contact for key in ['id', 'name', 'email', 'subject', 'message', 'created_at']):
                raise ValueError("Missing expected fields in the contact data.")
        
        print(contacts)

    except requests.RequestException as e:
        contacts = []  
        print("Error fetching data from Flask API:", e)
    except ValueError as ve:
        contacts = []
        print("Data validation error:", ve)

    return render(request, "contact_messages.html", context={"contacts": contacts})

















