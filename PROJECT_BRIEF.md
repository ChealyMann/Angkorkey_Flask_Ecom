# Project Brief

## Project Goal
Angkorkey is a Flask-based e-commerce web application that allows users to browse and search for products, view details, and manage a shopping cart, while providing an administration interface for managing content.

## Tech Stack
- **Language:** Python
- **Framework:** Flask (using Blueprints)
- **Database:** SQLAlchemy (ORM) with SQLite (development)
- **Migrations:** Flask-Migrate (Alembic)
- **Forms:** Flask-WTF
- **Frontend:** Jinja2 Templates, HTML5, CSS3, JavaScript (likely Bootstrap based on typical Flask usage and `bs4` references)
- **Utilities:** Werkzeug (security), Click (CLI commands)

## Architecture
The project follows a **Modular MVC (Model-View-Controller)** pattern adapted for Flask using **Blueprints**.

- **Folder Structure:**
  - `app.py`: Application entry point and configuration.
  - `blueprint/`: Contains the application logic (Controllers/Views) separated by domain (`home`, `admin`, `product`).
  - `models/`: Database models (`User`, `Product`, `Category`).
  - `templates/`: Jinja2 HTML templates, organized into `frontend` and `backend` (admin).
  - `static/`: Static assets (CSS, JS, images).
  - `form/`: WTForms definitions for validation.
  - `migrations/`: Database migration scripts.

## Coding Conventions
- **Style:** Pythonic style following PEP 8.
- **Indentation:** 4 spaces.
- **Naming:**
  - **Variables/Functions:** `snake_case` (e.g., `product_detail`, `search_query`).
  - **Classes:** `PascalCase` (e.g., `User`, `LoginForm`).
  - **Constants:** `UPPER_CASE` (e.g., `SECRET_KEY`).
- **ORM:** Usage of SQLAlchemy `db.Model` and query methods (e.g., `User.query.filter_by(...)`).
- **Templating:** Semantic separation of frontend and backend layouts.

## Core Features
- **Public Storefront:**
  - **Home Page:** Featured/recent products.
  - **Product Catalog:** List view with pagination, category filtering, and AJAX-based search.
  - **Product Detail:** Dedicated page for individual product information.
  - **Shopping Cart:** Interface for cart management (route `/cart`).
- **User Management:**
  - **Authentication:** Login and Registration with password hashing.
  - **Profile:** User data includes username, phone, and profile image.
- **Administration:**
  - Protected admin routes (requires login).
  - Dashboard for managing resources (inferred from `admin_bp`).
- **System:**
  - **Data Migration:** Database schema management via Flask-Migrate.
  - **File Uploads:** Image upload and processing services.
  - **CLI Commands:** Custom commands (e.g., `create-admin`).
