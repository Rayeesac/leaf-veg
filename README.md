# LEAFS Exotic Vegetables

A Django web application for wholesale B2B pre-ordering of fresh Chinese produce. Buyers browse the catalog, select quantities in kilograms, submit their pre-order, and immediately receive a printable/downloadable invoice. Administrators manage inventory, update order statuses, and generate pack-up batch reports.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+ / Django 5.1 |
| Database | PostgreSQL |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| PDF Generation | WeasyPrint 62 |
| Image Handling | Pillow 11 |
| Config | python-decouple |

---

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- pip

### 1. Clone and set up environment

```bash
git clone <repository-url>
cd leafs-vegetables
bash setup.sh
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your database credentials and a secure SECRET_KEY
```

**Never commit `.env` to version control.** See `.env.example` for required variables.

### 3. Create PostgreSQL database

```bash
createdb leafs_vegetables
```

### 4. Run migrations

```bash
source venv/bin/activate
python manage.py migrate
```

### 5. Create admin superuser

```bash
python manage.py createsuperuser
```

### 6. Load demo data (optional)

```bash
python manage.py seed_demo_data
```

### 7. Start development server

```bash
python manage.py runserver 127.0.0.1:8000
```

Access the site at **http://127.0.0.1:8000/**  
Admin panel at **http://127.0.0.1:8000/admin/**

---

## Project Structure

```
leafs-vegetables/
├── leafs/                    # Django project configuration
│   ├── settings.py           # All settings (reads from .env)
│   ├── urls.py               # Root URL configuration
│   └── wsgi.py
├── catalog/                  # Core application
│   ├── models.py             # Vegetable, PreOrder, OrderItem models
│   ├── views.py              # Catalog, order submission, invoice views
│   ├── forms.py              # PreOrderForm, CartItemData validation
│   ├── admin.py              # Admin panel with pack-up report
│   ├── urls.py               # App URL patterns
│   ├── migrations/
│   └── management/
│       └── commands/
│           └── seed_demo_data.py
├── templates/
│   ├── base.html             # Site-wide base template
│   ├── catalog/
│   │   ├── catalog.html      # Product grid + order drawer
│   │   ├── confirmation.html # Order confirmation page
│   │   └── invoice.html      # Printable/PDF invoice
│   └── admin/
│       └── catalog/
│           └── packup_report.html
├── static/
│   ├── css/
│   │   ├── main.css          # Global styles
│   │   ├── catalog.css       # Catalog page styles
│   │   ├── confirmation.css  # Confirmation page styles
│   │   └── invoice.css       # Invoice + print styles
│   └── js/
│       └── catalog.js        # Cart engine
├── media/                    # Uploaded vegetable images (gitignored)
├── requirements.txt
├── .env.example
├── setup.sh
└── manage.py
```

---

## Features

### Buyer-Facing
- **Product catalog** — Card grid with image, SKU, price/kg, stock status
- **Category filtering** — Tab-based filter (Leafy Greens, Cabbages, Herbs, etc.)
- **Decimal weight inputs** — Enter e.g. `2.5 kg`, `50 kg` with +/− buttons
- **Live subtotals** — Line-item and grand total update in real time
- **Persistent order drawer** — Sidebar on desktop, slide-up FAB on mobile
- **Buyer info form** — Business name, contact, phone, pickup date, notes
- **Order confirmation** — Full breakdown with unique order code (`LCV-YYYY-NNNNN`)
- **Printable invoice** — Clean invoice with `@media print` CSS, full A4 layout
- **PDF download** — WeasyPrint-rendered PDF invoice

### Admin Panel (`/admin/`)
- **Vegetable CRUD** — Create, edit, hide vegetables; bulk stock toggle actions
- **Image preview** inline on vegetable detail page
- **Order list** — Filterable by date, status; sortable; date hierarchy nav
- **Inline order items** on each order detail page
- **Status update actions** — Bulk mark Packed / Ready / Completed / Cancelled
- **Invoice link** — Direct link to invoice from each order's admin page
- **Pack-Up Batch Report** — `/admin/catalog/preorder/packup-report/?date=YYYY-MM-DD`
  - Total kg per vegetable across all active orders on a given date
  - Printable report layout

---

## URL Reference

| URL | View | Description |
|---|---|---|
| `/` | `catalog` | Product catalog + order form |
| `/order/submit/` | `submit_order` | POST — process order submission |
| `/order/<ORDER_NUM>/confirmation/` | `order_confirmation` | Order confirmed page |
| `/order/<ORDER_NUM>/invoice/` | `invoice_print` | Printable HTML invoice |
| `/order/<ORDER_NUM>/invoice/pdf/` | `invoice_pdf` | Download PDF invoice |
| `/admin/` | Django admin | Management panel |
| `/admin/catalog/preorder/packup-report/` | Admin view | Pack-up batch report |

---

## Security Notes

- Secrets are loaded from environment variables via `python-decouple` — never hardcoded
- PostgreSQL binds to `127.0.0.1` (not `0.0.0.0`)
- Production settings enforce `SECURE_SSL_REDIRECT`, `HSTS`, `CSRF_COOKIE_SECURE`, `SESSION_COOKIE_SECURE`
- All user inputs validated server-side (cart JSON, form fields, date ranges)
- Structured JSON logging — no sensitive data in logs
- Parameterised ORM queries — no raw SQL string interpolation
- Vegetable delete is `PROTECT`-ed: orders referencing it cannot be deleted accidentally
