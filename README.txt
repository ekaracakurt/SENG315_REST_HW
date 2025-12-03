===============================================
 E-COMMERCE CART & NOTIFICATION SERVICE  
 Django REST Framework + Celery + Redis  
===============================================

This project implements a 3-layer backend architecture:

1. API Layer (REST) — Django REST Framework  
2. Messaging Layer — Celery + Redis (Async task processing)  
3. Data Layer — Django ORM + SQLite  

Users can add products to a cart, create orders, and Celery generates
notifications asynchronously via Redis.

This README explains:
- Project structure
- How the app works
- Running locally
- Running with Docker (Django + Celery + Redis)
- API usage  
===============================================================


===============================================================
 1. TECHNOLOGIES
===============================================================
Language: Python  
Framework: Django + DRF  
Messaging: Celery  
Broker / Queue: Redis  
Database: SQLite (default)  
Containers: Docker + Docker Compose  


===============================================================
 2. ARCHITECTURE OVERVIEW
===============================================================

--------------------
 API LAYER (REST)
--------------------
Implemented with Django REST Framework.

Endpoints include:
- GET /api/products/
- GET /api/cart/
- POST /api/cart-items/
- POST /api/orders/
- GET /api/notifications/

The API layer interacts with:
- Django ORM (data)
- Celery tasks (messaging)


-----------------------------
 MESSAGING LAYER (CELERY)
-----------------------------
When an order is created, the API triggers:

    send_order_created_notification.delay(order.id)

Celery:
- Serializes the task
- Sends it to Redis
- Worker receives and executes it asynchronously

Example task:

    @shared_task
    def send_order_created_notification(order_id):
        order = Order.objects.get(id=order_id)
        Notification.objects.create(
            order=order,
            type="ORDER_CREATED",
            message=f"Order #{order.id} created."
        )


-----------------------------
 DATA LAYER (ORM)
-----------------------------
Core models:
- Product
- Cart
- CartItem
- Order
- OrderItem
- Notification

SQLite is used by default for simplicity.


===============================================================
 3. CELERY CONFIGURATION
===============================================================

Environment-driven settings in config/settings.py:

    CELERY_BROKER_URL = os.environ.get(
        'CELERY_BROKER_URL',
        'redis://localhost:6379/0'
    )

    CELERY_RESULT_BACKEND = os.environ.get(
        'CELERY_RESULT_BACKEND',
        'redis://localhost:6379/1'
    )

This allows Celery to work:
- Locally (Redis on localhost)
- In Docker (Redis container)


===============================================================
 4. RUNNING LOCALLY (WITHOUT DOCKER)
===============================================================

(1) Create virtual environment:

    python -m venv venv
    venv\Scripts\activate   (Windows)

(2) Install dependencies:

    pip install -r requirements.txt

(3) Apply migrations:

    python manage.py migrate

(4) Create admin user:

    python manage.py createsuperuser

(5) Start Django backend:

    python manage.py runserver
    → http://127.0.0.1:8000/

(6) Start Celery worker:
Windows requires SOLO mode:

    celery -A config worker -l info -P solo

Linux/macOS:

    celery -A config worker -l info

===============================================================
 5. USING DOCKER (RECOMMENDED)
===============================================================

Project includes:
- Dockerfile
- docker-compose.yml

----------------------
 DOCKERFILE
----------------------
The Dockerfile builds an image that runs Django + Celery:

    FROM python:3.12-slim
    ENV PYTHONDONTWRITEBYTECODE=1
    ENV PYTHONUNBUFFERED=1
    WORKDIR /app
    RUN apt-get update && apt-get install -y build-essential
    COPY requirements.txt /app/
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . /app/
    CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


----------------------
 DOCKER-COMPOSE
----------------------
docker-compose.yml defines 3 services:

- web    → Django (runserver)
- worker → Celery worker
- redis  → Redis broker

Run all services:

    docker compose up --build

Access:
- API → http://127.0.0.1:8000/api/
- Admin → http://127.0.0.1:8000/admin/
*********************************************
Credentials for http://127.0.0.1:8000/admin/
inside docker image we give to the lecturers
*********************************************
***** Username: admin ***********************
***** Password: password123 *****************
*********************************************
*********************************************

Stop services:

    docker compose down


===============================================================
 6. FIRST-TIME SUPERUSER (INSIDE DOCKER)
===============================================================

    docker compose run --rm web python manage.py createsuperuser


===============================================================
 7. API TESTING WORKFLOW (EXAMPLE)
===============================================================

1. Create a product (via /admin/)
2. Add item to cart:

POST /api/cart-items/
{
  "product_id": 1,
  "quantity": 2
}

3. Create order:

POST /api/orders/

4. Celery worker creates a Notification automatically
5. View notifications:

GET /api/notifications/


===============================================================
 8. NOTES
===============================================================
- This uses Django's runserver (OK for development / university use).
- SQLite is fine for demo, but can be switched to PostgreSQL.
- Redis must be reachable from both Celery + Django.
- This architecture matches required 3-layer model:
  API (DRF)
  Messaging (Celery + Redis)
  Data (ORM)


===============================================================
 END OF FILE
===============================================================
