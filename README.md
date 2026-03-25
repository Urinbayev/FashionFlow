# FashionFlow - Fashion E-Commerce Platform

A modern, production-grade fashion e-commerce platform featuring virtual try-on concepts, AI-powered outfit recommendations, style profiles, seasonal collections, comprehensive size guides, and influencer partnership management.

## Architecture

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.x + Django REST Framework |
| Frontend | Vue.js 3 (Composition API) + Pinia-style Vuex 4 |
| Database | PostgreSQL 16 |
| Cache / Broker | Redis 7 |
| Task Queue | Celery 5 |
| Reverse Proxy | Nginx |
| Containerization | Docker + Docker Compose |

## Features

### Customer-Facing
- **Product Catalog** - Browse by category, collection, season, brand, color, and size
- **Virtual Try-On** - Upload a photo and visualize how garments look on you
- **Outfit Builder** - Mix and match products into complete outfits
- **Style Profiles** - Personalized style questionnaire powering recommendations
- **Style Boards** - Pinterest-style boards to save and share outfit inspiration
- **Size Guide** - Detailed measurement-based size recommendations per product
- **Seasonal Collections** - Curated product groupings by season and trend
- **Reviews & Ratings** - Photo reviews with fit feedback (runs small/true/large)
- **Promotions** - Coupon codes, flash sales, and percentage/fixed discounts
- **Order Management** - Full lifecycle from cart to delivery with return/refund support

### Admin / Business
- **Influencer Partnerships** - Track influencer codes, commissions, and performance
- **Inventory Management** - Per-variant stock tracking with low-stock alerts
- **Analytics Dashboard** - Sales, conversion, and product performance metrics
- **Promotion Engine** - Create and schedule coupons, flash sales, and campaigns

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### 1. Clone and Configure

```bash
git clone https://github.com/your-org/fashionflow.git
cd fashionflow
cp .env.example .env
```

Edit `.env` with your own secrets before proceeding.

### 2. Build and Run

```bash
docker-compose up --build -d
```

### 3. Initialize the Database

```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --noinput
```

### 4. Access the Application

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| API | http://localhost/api/ |
| Admin | http://localhost/admin/ |
| API Docs | http://localhost/api/docs/ |

## Project Structure

```
fashionflow/
├── backend/
│   ├── apps/
│   │   ├── accounts/      # User management, style profiles, addresses
│   │   ├── products/       # Catalog, categories, collections, variants
│   │   ├── orders/         # Orders, returns, refunds
│   │   ├── outfits/        # Outfit builder, style boards
│   │   ├── reviews/        # Product reviews and ratings
│   │   └── promotions/     # Coupons, flash sales, influencer codes
│   ├── config/
│   │   ├── settings/       # Split settings (base, dev, prod)
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── celery.py
│   ├── utils/              # Shared utilities
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/            # Axios API client modules
│   │   ├── components/     # Reusable Vue components
│   │   ├── views/          # Page-level components
│   │   ├── router/         # Vue Router configuration
│   │   ├── store/          # Vuex store modules
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/accounts/register/` | Register a new user |
| POST | `/api/accounts/login/` | Obtain JWT token pair |
| POST | `/api/accounts/token/refresh/` | Refresh access token |
| GET | `/api/accounts/profile/` | Get current user profile |
| PUT | `/api/accounts/style-profile/` | Update style profile |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products/` | List products (filterable) |
| GET | `/api/products/{slug}/` | Product detail |
| GET | `/api/products/categories/` | List categories |
| GET | `/api/products/collections/` | List collections |
| GET | `/api/products/collections/{slug}/` | Collection detail |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/orders/` | Create order |
| GET | `/api/orders/` | List user orders |
| GET | `/api/orders/{id}/` | Order detail |
| POST | `/api/orders/{id}/cancel/` | Cancel order |
| POST | `/api/orders/{id}/return/` | Request return |

### Outfits
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/outfits/` | List outfits |
| POST | `/api/outfits/` | Create outfit |
| GET | `/api/outfits/boards/` | List style boards |
| POST | `/api/outfits/boards/` | Create style board |

### Reviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reviews/?product={id}` | List product reviews |
| POST | `/api/reviews/` | Create review |

### Promotions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/promotions/validate/` | Validate a coupon code |
| GET | `/api/promotions/flash-sales/` | Active flash sales |

## Development

### Running Tests

```bash
docker-compose exec backend python manage.py test
```

### Code Quality

```bash
docker-compose exec backend flake8 .
docker-compose exec backend black --check .
```

### Frontend Development (Hot Reload)

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

See `.env.example` for all available configuration options. Key variables:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `ALLOWED_HOSTS` | Comma-separated allowed hostnames |
| `CORS_ALLOWED_ORIGINS` | Comma-separated CORS origins |
| `STRIPE_SECRET_KEY` | Stripe API secret key |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket for media files |

## Deployment

1. Set all production environment variables in `.env`
2. Ensure `DJANGO_SETTINGS_MODULE=config.settings.production`
3. Run `docker-compose -f docker-compose.yml up --build -d`
4. Run migrations and collect static files
5. Configure your DNS to point to the server
6. Set up SSL certificates (e.g., via Certbot)

## License

This project is proprietary software. All rights reserved.
