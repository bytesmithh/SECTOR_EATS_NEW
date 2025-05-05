from flask import Flask, render_template, redirect, url_for, request, flash,jsonify,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import joinedload
from functools import wraps
from datetime import datetime
from flask_restful import Resource,Api, reqparse
from flask_jwt_extended import JWTManager,create_access_token,get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_cors import CORS
import requests
import os


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # This is used to encode/decode the JWT
jwt = JWTManager(app)
api = Api(app)
CORS(app)  



UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"
UNSPLASH_ACCESS_KEY = "ZHIJbZdKPiPucflaNNgtvW0UQvv97NZhhqmyiseTxRM"


def get_food_image(food_name):
    url = f"https://api.unsplash.com/search/photos?query={food_name}+food&client_id={UNSPLASH_ACCESS_KEY}&per_page=1"
    response = requests.get(url).json()
    
    if response["results"]:
        return response["results"][0]["urls"]["regular"]  
    return "https://via.placeholder.com/400x300.png?text=No+Image" 


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "login"

class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50), nullable=False)  
    email = db.Column(db.String(100), unique=True, nullable=False)
    address= db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)  
    city = db.Column(db.String(15), nullable=False)  
    role = db.Column(db.String(10), default="user", nullable=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
class Restaurant(db.Model):
    __tablename__="restaurants"

    rid=db.Column(db.Integer, primary_key=True)
    rname= db.Column(db.String(50),nullable=False)
    raddress = db.Column(db.String(100),nullable=False)
    image_filename = db.Column(db.String(200), nullable=True)

class MenuItem(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    restaurant_id = db.Column(
        db.Integer, 
        db.ForeignKey('restaurants.rid', ondelete="CASCADE"), 
        nullable=False
    )
    restaurant = db.relationship('Restaurant', backref=db.backref('menu_items', lazy=True))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref="orders")  
    order_items = db.relationship('OrderItem', backref='order', lazy=True)
    
    @property
    def total_price(self):
        return sum(item.quantity * item.price for item in self.order_items)





class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
   
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    menu_item = db.relationship("MenuItem", backref="order_items")  


   

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False) 
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    menu_item = db.relationship("MenuItem", backref="cart_items")  

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User,int(user_id))

with app.app_context():
    db.create_all()

@app.route('/check_mobile', methods=['POST'])
def check_mobile():
    data = request.get_json()
    mobile = data.get('mobile')

    
    user = User.query.filter_by(mobile=mobile).first()
    if user:
        return jsonify({'exists': True})  
    else:
        return jsonify({'exists': False})  

@app.route('/login_mobile', methods=['GET','POST'])
def login_mobile():
    if request.method=="POST":
     mobile = request.form.get('mobile_login')
     password = request.form.get('password')
     user = User.query.filter_by(mobile=mobile).first()
     if not user:
         return "Mobile number does not exist!", 400

     
     if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("user_dashboard"))
     else:
      flash("Invalid password.", "danger")
      return render_template("login.html")

import requests

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")

            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("user_dashboard2"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        address=request.form.get("address")
        confirm_password = request.form.get("confirm_password")
        mobile = request.form.get("mobile")
        role=request.form.get("role")
        city=request.form.get("city")

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("signup"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect(url_for("signup"))
        
        

        new_user = User(name=name, email=email, mobile=mobile,role=role,address=address,city=city)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

def admin_required(func):
    @wraps(func)
    @login_required  
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Access denied!", "danger")
            return redirect(url_for('user_dashboard'))
        return func(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/about_us")
def about_us():
    return render_template("about_us.html")

@app.route("/best_seller")
def best_seller():
    return render_template("bestseller.html")

@app.route("/admin_dashboard")
@admin_required
@login_required
def admin_dashboard():
    user = User.query.filter_by(email=current_user.email).first()
    if current_user.role != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login")) 

    return render_template("dashboardadmin.html",mail=user.email)

@app.route('/delete_restaurant/<int:rid>', methods=['POST'])
@admin_required
@login_required
def delete_restaurant(rid):
    restaurant = Restaurant.query.get_or_404(rid)

    MenuItem.query.filter_by(restaurant_id=rid).delete()

  
    if restaurant.image_filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], restaurant.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(restaurant)
    db.session.commit()
    
    flash('Restaurant deleted successfully!', 'success')
    return redirect(url_for('user_dashboard'))


@app.route('/edit_restaurant/<int:rid>', methods=['GET'])
@admin_required
def edit_restaurant(rid):
    restaurant = Restaurant.query.get_or_404(rid)
    return render_template('add_restaurant.html', restaurant=restaurant)


@app.route("/user_dashboard")
@login_required
def user_dashboard():
    user_city = current_user.city  
    restaurants = Restaurant.query.filter(Restaurant.raddress.ilike(f"%{user_city}%")).all()  
    return render_template("user_dashboard.html", restaurants=restaurants)

@app.route('/submit_restaurant', methods=['POST'])
@admin_required
def submit_restaurant():
    rid = request.form.get('rid')  
    rname = request.form['restaurant_name']
    raddress = request.form['restaurant_address']
    
    image = request.files['restaurant_image']
    
    if rid: 
        restaurant = Restaurant.query.get_or_404(rid)
        restaurant.rname = rname
        restaurant.raddress = raddress
        
        if image: 
            old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], restaurant.image_filename)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
            
            image_filename = image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            restaurant.image_filename = image_filename
        
        flash('Restaurant updated successfully!', 'success')
    else:  
        image_filename = image.filename if image else None
        if image:
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        restaurant = Restaurant(rname=rname, raddress=raddress, image_filename=image_filename)
        db.session.add(restaurant)
        flash('Restaurant added successfully!', 'success')

    db.session.commit()
    return redirect(url_for('add_restaurant'))

@app.route('/admin_dashboard/add_restaurant')
@admin_required
@login_required
def add_restaurant():
    return render_template('add_restaurant.html')


@app.route('/menu/<int:restaurant_id>')
@login_required
def view_menu(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()

    
    for item in menu_items:
        item.image_url = get_food_image(item.name)

    return render_template("menu.html", restaurant=restaurant, menu_items=menu_items)


@app.route('/menu/edit/<int:restaurant_id>', methods=['GET', 'POST'])
@admin_required
def edit_menu(restaurant_id):
    if current_user.role != 'admin':
        flash("You are not authorized!", "danger")
        return redirect(url_for('view_menu', restaurant_id=restaurant_id))

    restaurant = Restaurant.query.get_or_404(restaurant_id)

    if request.method == 'POST':
        item_name = request.form['item_name']
        price = request.form['price']
        new_item = MenuItem(name=item_name, price=price, restaurant_id=restaurant_id)
        db.session.add(new_item)
        db.session.commit()
        flash("Menu item added!", "success")
        return redirect(url_for('edit_menu', restaurant_id=restaurant_id))

    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    return render_template('edit_menu.html', restaurant=restaurant, menu_items=menu_items)

@app.route('/update_menu_item/<int:item_id>', methods=['POST'])
@admin_required
def update_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    
    item.name = request.form['item_name']
    item.price = request.form['price']

    db.session.commit()
    flash("Menu item updated successfully!", "success")

    return redirect(url_for('edit_menu', restaurant_id=item.restaurant_id))

@app.route('/cart')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    
    total_price = sum(item.quantity * item.menu_item.price for item in cart_items if item.menu_item)

    return render_template("cart.html", cart_items=cart_items, total_price=total_price)


@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = Cart.query.get_or_404(item_id)
    
    if item.user_id != current_user.id:
        flash("Unauthorized action!", "danger")
        return redirect(url_for('cart'))

    db.session.delete(item)
    db.session.commit()

    flash("Item removed from cart!", "success")
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        flash("Your cart is empty!", "danger")
        return redirect(url_for('cart'))

    
    new_order = Order(
        user_id=current_user.id,
        status="Pending",
        timestamp=datetime.utcnow()
    )
    db.session.add(new_order)
    db.session.commit()  


    for item in cart_items:
        for _ in range(item.quantity):  
            order_item = OrderItem(
                order_id=new_order.id,
                menu_item_id=item.item_id,  
                name=item.name,  
                price=item.price,  
                quantity=1  
            )
            db.session.add(order_item)

  
    Cart.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()

    flash("Order placed successfully!", "success")
    return redirect(url_for('my_orders'))



@app.route('/change_address', methods=['POST'])
@login_required
def change_address():
    new_address = request.form.get('new_address')
    if new_address:
        current_user.address = new_address  
        db.session.commit() 
        flash('Address updated successfully!', 'success')
    else:
        flash('Please enter a valid address.', 'danger')

    return redirect(url_for('user_dashboard'))  


from sqlalchemy import not_

@app.route('/admin_dashboard/orders')
@admin_required
@login_required
def orders_admin():
    orders = Order.query.options(joinedload(Order.order_items).joinedload(OrderItem.menu_item))\
        .filter(Order.status != "Delivered").all()
    return render_template("orders_admin.html", orders=orders)

    
@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    item_id = request.form.get('item_id')
    quantity = int(request.form.get('quantity', 1))  

    if not item_id or quantity <= 0:
        flash("Invalid item or quantity!", "danger")
        return redirect(url_for('user_dashboard'))

    # Fetch the menu item from database
    menu_item = MenuItem.query.get(item_id)
    if not menu_item:
        flash("Menu item not found!", "danger")
        return redirect(url_for('user_dashboard'))

   
    existing_cart_item = Cart.query.filter_by(user_id=current_user.id, item_id=item_id).first()

    if existing_cart_item:
        existing_cart_item.quantity = min(5, existing_cart_item.quantity + quantity)  
    else:
        
        new_cart_item = Cart(
            user_id=current_user.id,
            item_id=menu_item.id,
            name=menu_item.name,
            price=menu_item.price,
            quantity=quantity
        )
        db.session.add(new_cart_item)

    db.session.commit()
    flash(f"{menu_item.name} added to cart!", "success")
    return redirect(url_for('view_menu', restaurant_id=menu_item.restaurant_id))

@app.route('/update_order_status/<int:order_id>', methods=['POST'])
@admin_required
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get("status")

    if new_status not in ["Pending", "Accepted", "Being Prepared", "Out for Delivery", "Delivered"]:
        flash("Invalid status!", "danger")
        return redirect(url_for('orders_admin'))

    order.status = new_status
    db.session.commit()

    flash("Order status updated successfully!", "success")
    return redirect(url_for('orders_admin'))

@app.route('/my_orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()  
    return render_template("my_orders.html", orders=orders)


@app.route('/order_details/<int:order_id>')
@login_required
def order_details(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    order_data = {
        'id': order.id,
        'user': order.user.name,
        'status': order.status,
        'total_price': order.total_price,
        'items': [
            {'name': item.menu_item.name, 'quantity': item.quantity, 'price': item.price}
            for item in order.order_items
        ]
    }
    return jsonify(order_data)

@app.route('/update_cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    new_quantity = request.form.get('quantity', type=int)

    if new_quantity is None or new_quantity < 1:
        flash("Quantity must be at least 1.", "warning")
    elif new_quantity > 5:
        flash("You can't add more than 5 of the same item.", "warning")
    else:
        cart_item = Cart.query.filter_by(id=item_id, user_id=current_user.id).first()
        if cart_item:
            cart_item.quantity = new_quantity
            db.session.commit()
            flash("Cart updated successfully!", "success")
        else:
            flash("Item not found in cart.", "danger")

    return redirect(url_for('cart'))


class RegisterResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, help="Name cannot be blank")
        parser.add_argument('email', required=True, help="Email cannot be blank")
        parser.add_argument('address', required=True, help="Address cannot be blank")
        parser.add_argument('mobile', required=True, help="Mobile cannot be blank")
        parser.add_argument('city', required=True, help="City cannot be blank")
        parser.add_argument('role', required=False, default="user", help="Role, default is user")
        parser.add_argument('password', required=True, help="Password cannot be blank")
        
        args = parser.parse_args()

        # Check if user already exists
        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already exists'}, 400

        # Create new user instance
        new_user = User(
            name=args['name'],
            email=args['email'],
            address=args['address'],
            mobile=args['mobile'],
            city=args['city'],
            role=args['role']
        )

        # Hash password and save
        new_user.set_password(args['password'])
        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User registered successfully'}, 201



class LoginResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help="Email cannot be blank")
        parser.add_argument('password', required=True, help="Password cannot be blank")

        args = parser.parse_args()

        # Fetch user from DB by email
        user = User.query.filter_by(email=args['email']).first()

        if not user or not user.check_password(args['password']):
            return {'message': 'Invalid credentials'}, 401

        # Generate JWT token
        access_token = create_access_token(identity=user.email)

        return {'access_token': access_token}, 200


class UserProfileResource(Resource):
    @jwt_required()
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'address': user.address,
            'mobile': user.mobile,
            'city': user.city,
            'role': user.role
        })

    @jwt_required()
    def put(self, user_id):
        user = User.query.get_or_404(user_id)

        # Ensure the logged-in user can only update their own profile
        if user.id != get_jwt_identity():  # Verify identity with JWT
            return {'message': 'Unauthorized access'}, 403

        data = request.get_json()

        user.name = data.get('name', user.name)
        user.email = data.get('email', user.email)
        user.address = data.get('address', user.address)
        user.mobile = data.get('mobile', user.mobile)
        user.city = data.get('city', user.city)
        user.role = data.get('role', user.role)

        # Update password if provided
        if 'password' in data:
            user.set_password(data['password'])

        db.session.commit()

        return jsonify({'message': 'User updated successfully'})



# Restaurant Resource
class RestaurantResource(Resource):
    def get(self, rid):
        restaurant = Restaurant.query.get_or_404(rid)
        return jsonify({
            'id': restaurant.rid,
            'name': restaurant.rname,
            'address': restaurant.raddress,
            'image_filename': restaurant.image_filename
        })

    def put(self, rid):
        restaurant = Restaurant.query.get_or_404(rid)
        data = request.get_json()

        restaurant.rname = data.get('rname', restaurant.rname)
        restaurant.raddress = data.get('raddress', restaurant.raddress)
        db.session.commit()

        return jsonify({'message': 'Restaurant updated successfully'})

    def delete(self, rid):
        restaurant = Restaurant.query.get_or_404(rid)
        db.session.delete(restaurant)
        db.session.commit()
        return jsonify({'message': 'Restaurant deleted successfully'})


# View all users Resource
class AllUsersResource(Resource):
    @jwt_required()  # Require JWT to access this route
    def get(self):
        users = User.query.all()
        return jsonify([{
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'address': user.address,
            'mobile': user.mobile,
            'city': user.city,
            'role': user.role
        } for user in users])


# View all restaurants Resource
class AllRestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([{
            'id': restaurant.rid,
            'name': restaurant.rname,
            'address': restaurant.raddress,
            'image_url': request.host_url + 'static/uploads/' + restaurant.image_filename if restaurant.image_filename else None
        } for restaurant in restaurants])

class MenuItemResource(Resource):
    def get(self, restaurant_id):
        menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
        return jsonify([{
            'id': menu_item.id,
            'name': menu_item.name,
            'price': menu_item.price,
            'restaurant_id': menu_item.restaurant_id
        } for menu_item in menu_items])
    
    def post(self):
        data = request.get_json()
        name = data.get('name')
        price = data.get('price')
        restaurant_id = data.get('restaurant_id')

        new_item = MenuItem(name=name, price=price, restaurant_id=restaurant_id)
        db.session.add(new_item)
        db.session.commit()

        return jsonify({'message': 'Menu item created successfully', 'item_id': new_item.id})


class AllOrdersResource(Resource):
    def get(self, order_id=None):
        if order_id:
            order = Order.query.get(order_id)
            if not order:
                return jsonify({'message': 'Order not found'}), 404
            return jsonify({
                'order_id': order.id,
                'user_id': order.user_id,
                'status': order.status,
                'timestamp': order.timestamp,
                'total_price': order.total_price,
                'order_items': [{
                    'item_id': item.id,
                    'name': item.name,
                    'price': item.price,
                    'quantity': item.quantity,
                    'menu_item_id': item.menu_item_id,
                    'menu_item_name': item.menu_item.name
                } for item in order.order_items]
            })

        orders = Order.query.all()


        return jsonify([{
            'order_id': order.id,
            'user_id': order.user_id,
            'status': order.status,
            'timestamp': order.timestamp,
            'total_price': order.total_price,
            'order_items': [{
                'item_id': item.id,
                'name': item.name,
                'price': item.price,
                'quantity': item.quantity,
                'menu_item_id': item.menu_item_id,
                'menu_item_name': item.menu_item.name
            } for item in order.order_items]
        } for order in orders])


    



api.add_resource(RegisterResource, '/api/register')
api.add_resource(LoginResource, '/api/login')
api.add_resource(UserProfileResource, '/api/users/<int:user_id>')
api.add_resource(RestaurantResource, '/api/restaurants/<int:rid>')
api.add_resource(MenuItemResource, '/api/menu-items/restaurant/<int:restaurant_id>')  
api.add_resource(AllUsersResource, '/api/users') 
api.add_resource(AllRestaurantsResource, '/api/restaurants')  
api.add_resource(AllOrdersResource, '/api/orders')




@app.route('/api/order', methods=['POST'])
def place_order():
    data = request.get_json()

    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"message": "Missing user_id"}), 400

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": f"User ID {user_id} not found in Flask DB"}), 400

        new_order = Order(user_id=user_id, status="Pending", timestamp=datetime.utcnow())
        db.session.add(new_order)
        db.session.flush()

        order_items = []
        total_amount = 0

        for item in data["items"]:
            order_item = OrderItem(
                order_id=new_order.id,
                name=item["name"],
                price=item["price"],
                quantity=item["quantity"],
                menu_item_id=item["id"]
            )
            db.session.add(order_item)
            order_items.append({
                "id": item["id"],  # Django MenuItem ID
                "name": item["name"],
                "price": item["price"],
                "quantity": item["quantity"]
            })
            total_amount += item["price"] * item["quantity"]

        db.session.commit()

        return jsonify({"message": "Order placed successfully", "order_id": new_order.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

    
@app.route('/api/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    user_id = data.get("id")

    # Avoid duplicate users
    existing_user = User.query.get(user_id)
    if existing_user:
        return jsonify({"message": "User already exists"}), 200

    try:
        new_user = User(
            id=user_id,
            name=data.get("name"),
            email=data.get("email"),
            address=data.get("address"),
            city=data.get("city"),
            mobile=data.get("mobile"),
            role=data.get("role"),
            password=data.get("password", "default")
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error creating user: {str(e)}"}), 500
    
class ContactUs(db.Model):

    __tablename__ = "contact_us"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ContactUs {self.id} - {self.name}>"
    

contact_parser = reqparse.RequestParser()
contact_parser.add_argument('name', type=str, required=True, help='Name is required')
contact_parser.add_argument('email', type=str, required=True, help='Email is required')
contact_parser.add_argument('subject', type=str, required=True, help='Subject is required')
contact_parser.add_argument('message', type=str, required=True, help='Message is required')

class ContactUsResource(Resource):
    def get(self):
        contacts = ContactUs.query.order_by(ContactUs.created_at.desc()).all()
        return jsonify([{
            'id': contact.id,
            'name': contact.name,
            'email': contact.email,
            'subject': contact.subject,
            'message': contact.message,
            'created_at': contact.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for contact in contacts])

    def post(self):
        args = contact_parser.parse_args()

        new_contact = ContactUs(
            name=args['name'],
            email=args['email'],
            subject=args['subject'],
            message=args['message']
        )

        db.session.add(new_contact)
        db.session.commit()

        return {'message': 'Contact form submitted successfully'}, 201
    
api.add_resource(ContactUsResource, '/api/contact')


@app.route("/user_dashboard2")
@login_required
def user_dashboard2():
    return render_template("kfc.html")

@app.route('/contact', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Create a new ContactUs instance
        new_message = ContactUs(name=name, email=email, subject=subject, message=message)

        # Add and commit to the database
        db.session.add(new_message)
        db.session.commit()

        flash('Your message has been sent!', 'success')
        return redirect(url_for('contact_us'))  

    return render_template('contact_us.html')  

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
