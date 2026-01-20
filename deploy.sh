#!/bin/bash
# Fly.io deployment script for ak-chars API

set -e  # Exit on error

echo "=========================================="
echo "Fly.io Deployment Script"
echo "=========================================="
echo ""

# Step 1: Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl not found. Installing..."
    brew install flyctl
else
    echo "✓ flyctl is installed"
fi

# Step 2: Check if user is logged in
echo ""
echo "Checking authentication..."
if ! flyctl auth whoami &> /dev/null; then
    echo "Please login to Fly.io:"
    flyctl auth login
else
    echo "✓ Already logged in"
fi

# Step 3: Launch app (if not already created)
echo ""
echo "=========================================="
echo "Step 1: Creating app on Fly.io"
echo "=========================================="
echo "This will:"
echo "  - Create the app on Fly.io"
echo "  - Ask you to choose a region"
echo "  - NOT deploy yet"
echo ""
read -p "Press Enter to continue..."

flyctl launch --no-deploy

# Step 4: Set secrets
echo ""
echo "=========================================="
echo "Step 2: Setting environment variables"
echo "=========================================="
echo ""

# Get the app name from fly.toml
APP_NAME=$(grep "^app = " fly.toml | cut -d'"' -f2)
echo "App name: $APP_NAME"
echo ""

echo "Setting JWT_SECRET..."
flyctl secrets set JWT_SECRET=0b1dd73601787df8dd1a6c6c8e9007bbf9d1251afab9910d771ed61908896446

echo "Setting USE_FIXTURES to false (use live game API)..."
flyctl secrets set USE_FIXTURES=false

echo "Setting CORS_ORIGIN..."
echo ""
echo "Enter your frontend URL (e.g., https://your-app.vercel.app)"
echo "Or press Enter to skip and set it later:"
read -r CORS_ORIGIN
if [ -n "$CORS_ORIGIN" ]; then
    flyctl secrets set CORS_ORIGIN="$CORS_ORIGIN"
    echo "✓ CORS_ORIGIN set to: $CORS_ORIGIN"
else
    echo "⚠ Skipping CORS_ORIGIN - you can set it later with: flyctl secrets set CORS_ORIGIN=https://your-frontend.com"
fi

echo ""
echo "Do you want to configure SMTP for email functionality? (y/n)"
read -r CONFIGURE_SMTP
if [ "$CONFIGURE_SMTP" = "y" ]; then
    echo "Enter SMTP_HOST (e.g., smtp.gmail.com):"
    read -r SMTP_HOST
    echo "Enter SMTP_PORT (e.g., 587):"
    read -r SMTP_PORT
    echo "Enter SMTP_USER (your email):"
    read -r SMTP_USER
    echo "Enter SMTP_PASS (your app password):"
    read -rs SMTP_PASS

    flyctl secrets set SMTP_HOST="$SMTP_HOST"
    flyctl secrets set SMTP_PORT="$SMTP_PORT"
    flyctl secrets set SMTP_USER="$SMTP_USER"
    flyctl secrets set SMTP_PASS="$SMTP_PASS"

    echo ""
    echo "✓ SMTP credentials set"
else
    echo "⚠ Skipping SMTP - emails will be logged instead of sent"
fi

# Step 5: Deploy
echo ""
echo "=========================================="
echo "Step 3: Deploying to Fly.io"
echo "=========================================="
echo ""
read -p "Ready to deploy? Press Enter to continue..."

flyctl deploy

# Step 6: Show status
echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
flyctl status
echo ""
echo "Your API is live at: https://$APP_NAME.fly.dev"
echo ""
echo "Useful commands:"
echo "  flyctl logs          - View logs"
echo "  flyctl status        - Check app status"
echo "  flyctl ssh console   - SSH into your VM"
echo "  flyctl secrets list  - List environment variables"
echo ""
