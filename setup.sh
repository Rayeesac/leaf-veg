#!/usr/bin/env bash
# =============================================================
# LEAFS Chinese Vegetables — Initial Setup Script
# Run once after cloning to configure the project environment.
# =============================================================
set -e

echo "=== LEAFS Chinese Vegetables — Setup ==="

# 1. Check Python version
python_version=$(python3 --version 2>&1)
echo "Python: $python_version"

# 2. Create virtualenv (if not present)
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

# 3. Activate virtualenv
source venv/bin/activate

# 4. Upgrade pip and install dependencies
echo "Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# 5. Check .env file
if [ ! -f ".env" ]; then
  echo ""
  echo "⚠️  No .env file found. Copying .env.example to .env"
  cp .env.example .env
  echo "   Please edit .env with your database credentials and SECRET_KEY before continuing."
  echo ""
fi

# 6. Create media directory
mkdir -p media/vegetables

echo ""
echo "✅ Dependencies installed."
echo ""
echo "Next steps:"
echo "  1. Edit .env with your PostgreSQL credentials and a secure SECRET_KEY"
echo "  2. Create your PostgreSQL database:  createdb leafs_vegetables"
echo "  3. Run migrations:                   python manage.py migrate"
echo "  4. Create superuser:                 python manage.py createsuperuser"
echo "  5. Collect static files:             python manage.py collectstatic"
echo "  6. Start development server:         python manage.py runserver 127.0.0.1:8000"
