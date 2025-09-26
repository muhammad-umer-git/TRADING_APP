# Trading App

A Django REST API for stock trading simulation.  
Users can register, manage accounts, trade stocks, and generate daily reports with Celery.

---

## Tech Stack
- Python 3.11
- Django + Django REST Framework
- PostgreSQL (database)
- Redis (cache + Celery broker)
- Celery & Celery Beat (async tasks + scheduling)
- yfinance (stock price data source)

---

##  Features
- JWT Authentication (register/login)
- Account balances & positions
- Stock data (list + detail, cached in Redis)
- Trade system (buy/sell, atomic with row locking)
- Ledger entries for each trade
- Daily CSV reports (profit/loss, portfolio summary) via Celery

---

##  Setup

1. close repository
git clone (https://github.com/muhammad-umer-git/TRADING_APP.git)
cd core

2. Install dependencies
pip install -r requirements.txt

3. Configure database (in settings.py)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'trading_db',
        'USER': 'trading_user',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
4. Run migrations
python manage.py migrate

5. Create a superuser (optional)
python manage.py createsuperuser
(one already created)
(username: admin ,  password : admin)

6. Start Redis ( for cashe and celery)
redis-server

7. Start celery worker and beat in separate terminals
celery -A core worker -l info
celery -A core beat -l info

8. Start Django Development Server
python manage.py runserver

9. Access the app
- API: http://127.0.0.1:8000/ 
- Admin panel : http://127.0.0.1:8000/admin/