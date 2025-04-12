
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






from .forms import MenuItemForm


from .models import Profile,Restaurant,MenuItem,Cart, Order, OrderItem
from .forms import RestaurantForm



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
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect('login_view')

        user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            login(request, user)
            profile = Profile.objects.get(user=user)

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



#logic for Ai model integration

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
    user_profile = request.user.profile  # Assuming Profile has OneToOne with User
    user_city = user_profile.city.lower()

    restaurants = Restaurant.objects.filter(
        is_active=True,
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
        print("Form Submitted")  # debug

        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.admin = request.user
            restaurant.save()
            messages.success(request, 'Restaurant added successfully!')
            return redirect('admin_dashboard')
        else:
            print("Form errors:", form.errors)  # debug
    else:
        form = RestaurantForm()

    return render(request, 'add_restaurant.html', {'form': form})



@admin_required
@login_required
def list_restaurants(request):
    restaurants = Restaurant.objects.filter(admin=request.user)  # 👈 Only owned restaurants
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
            return redirect('list_restaurants')  # Or redirect to a restaurant detail page if you have it
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

    # Get quantity from GET parameters (default to 1 if not provided)
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


    # Assuming user has a profile with name, email, etc.
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

    # Fetch all orders
    orders = Order.objects.select_related('user').prefetch_related('items__item').order_by('-created_at')
    
    # Filter orders by status
    active_orders = orders.exclude(status__in=["Delivered", "Rejected"])  # Active orders
    delivered_orders = orders.filter(status="Delivered")  # Delivered orders
    rejected_orders = orders.filter(status="Rejected")  # Rejected orders

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
    # Fetch all feedback
    feedbacks = Feedback.objects.all().order_by('-submitted_at')  # Order by submission time, latest first
    return render(request, 'admin_feedback.html', {'feedbacks': feedbacks})

def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'order_detail.html', {'order': order})








