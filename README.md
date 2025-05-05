# Sector Eats 🍔

**Sector Eats** is a Django-based food ordering web application designed to streamline food delivery operations. It supports restaurant listings, menu management, cart & order systems, and includes intelligent features like AI-powered customer interaction and recommendation services.

---

## 🚀 Features

- User authentication (signup, login, logout)
- Browse restaurants and menus
- Add to cart and place orders
- Admin dashboard for restaurants
- Real-time order status tracking
- AI-powered chatbot for food-related queries
- Credit card animation form integration
- Clean UI with responsive design

---

## 🧠 Integrated APIs

### 1. 🤖 Hugging Face Inference API (AI Chatbot)

We’ve integrated a Hugging Face model via their Inference API to serve as a smart **AI chatbot** for customer support. Users can ask food-related questions or get recommendations in real-time.

- **Use case:** Responds to user queries (e.g., food suggestions, ingredients, delivery time).
- **Tech:** Hugging Face Inference API with a conversational NLP model.
- **Integration:** Django views handle API calls and display responses via the chatbot UI.

---

### 2. 🛠️ Flask RESTful API (Custom Microservice)

We’ve built a custom **Flask RESTful API** to handle features that are decoupled from the main Django app. This includes:

- **Recommendation Engine:** Suggest dishes based on past user orders.
- **Order Analytics:** Tracks and analyzes user order history.
- **Microservice Architecture:** Designed for scalability and modularity.

> Hosted independently and consumed by Django via HTTP requests (using `requests` library or AJAX).

---

## ⚙️ Tech Stack

- **Frontend:** HTML, Tailwind CSS, JavaScript
- **Backend:** Django (Python)
- **Database:** SQLite (for dev), PostgreSQL (recommended for production)
- **AI Integration:** Hugging Face Transformers
- **Microservices:** Flask with Flask-RESTful

---


---

## 🚧 Setup Instructions

1. **Clone the repo**  
   `git clone https://github.com/bytesmithh/SECTOR_EATS_NEW.git`

2. **Folder Selection**
  `Select the folder you want django or flask`
  
3. **Install dependencies**  
   `pip install -r requirements.txt`

4. **Run the server**  
   `python manage.py runserver`

5. **(Optional) Run Flask API**  
   Navigate to `flask_api/` and run:
   `python app.py`

---

## 💬 Future Enhancements

- Payment gateway integration
- Real-time delivery tracking with WebSockets
- Multi-language support
- Firebase push notifications

---





