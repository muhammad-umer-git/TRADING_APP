# Trading App

A Django REST API for stock trading simulation.  
Users can register, manage accounts, trade stocks, and generate daily reports with Celery.

---

## Tech Stack
- Python 3.12
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

1. Clone Repository
git clone https://github.com/muhammad-umer-git/TRADING_APP.git
cd TRADING_APP/core

2. Create Virtual Environment & Install Dependencies
python -m venv .venv
source .venv/bin/activate   # Linux / Mac
.venv\Scripts\activate      # Windows (PowerShell)

pip install -r requirements.txt

3. Configure Environment Variables

Create a .env file in the core/ directory with:

DEBUG=True
SECRET_KEY=your_secret_key_here

DB_NAME=trading_db
DB_USER=trading_user
DB_PASSWORD=mypassword
DB_HOST=localhost
DB_PORT=5432


4. Run Migrations
python manage.py migrate

5. Create Superuser (Optional)
python manage.py createsuperuser

(You can also use the default admin)
username:admin
password:admin

6. Start Redis (for cache & Celery)
redis-server

7. Start Celery Worker & Beat

Open two terminals:

celery -A core worker -l info
celery -A core beat -l info

8. Run Development Server
python manage.py runserver

9. Access the App

API: http://127.0.0.1:8000/

Admin Panel: http://127.0.0.1:8000/admin/

