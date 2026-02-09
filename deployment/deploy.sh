#!/bin/bash

# Napling Choice Awards Deployment Script
# This script automates the deployment process for production

set -e

echo "Starting deployment of Napling Choice Awards..."

# Configuration
PROJECT_DIR="/var/www/napling-choice-awards"
BACKUP_DIR="/var/backups/napling-choice-awards"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."
for cmd in git npm python3 pip mongod nginx; do
    if ! command_exists $cmd; then
        echo "Error: $cmd is not installed"
        exit 1
    fi
done

# Create project directory if it doesn't exist
echo "Setting up project directory..."
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR

# Backup current deployment if it exists
if [ -d "$PROJECT_DIR/backend" ] || [ -d "$PROJECT_DIR/frontend" ]; then
    echo "Creating backup of current deployment..."
    sudo cp -r $PROJECT_DIR $BACKUP_DIR/backup_$DATE
fi

# Clone or update the repository
echo "Setting up application files..."
if [ ! -d "$PROJECT_DIR/.git" ]; then
    git clone <YOUR_REPOSITORY_URL> $PROJECT_DIR
else
    cd $PROJECT_DIR
    git pull origin main
fi

# Backend setup
echo "Setting up backend..."
cd $PROJECT_DIR/backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Check if .env exists, copy from example if not
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Please edit $PROJECT_DIR/backend/.env with your configuration"
    exit 1
fi

# Initialize database if needed
echo "Initializing database..."
python database_setup.py

# Frontend setup
echo "Setting up frontend..."
cd $PROJECT_DIR/frontend

# Install dependencies and build
npm install
npm run build

# Set up nginx configuration
echo "Configuring nginx..."
sudo cp ../deployment/nginx.conf /etc/nginx/sites-available/napling-choice-awards
sudo ln -sf /etc/nginx/sites-available/napling-choice-awards /etc/nginx/sites-enabled/
sudo nginx -t

# Set up gunicorn service
echo "Configuring gunicorn service..."
sudo cp ../deployment/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable napling-choice-awards
sudo systemctl start napling-choice-awards

# Set proper permissions
echo "Setting permissions..."
sudo chown -R www-data:www-data $PROJECT_DIR/backend
sudo chmod -R 755 $PROJECT_DIR

# Restart services
echo "Restarting services..."
sudo systemctl restart nginx
sudo systemctl restart napling-choice-awards

# Check service status
echo "Checking service status..."
sudo systemctl status nginx --no-pager
sudo systemctl status napling-choice-awards --no-pager

echo "Deployment completed successfully!"
echo "Your application should now be available at your domain"
echo "Backup created at: $BACKUP_DIR/backup_$DATE"
