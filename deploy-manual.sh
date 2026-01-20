#!/bin/bash
# Manual deployment steps - run each command one at a time

echo "Step 1: Login to Fly.io"
echo "Run: flyctl auth login"
echo ""
echo "Step 2: Create app"
echo "Run: flyctl launch --no-deploy"
echo ""
echo "Step 3: Set secrets"
echo "Run: flyctl secrets set JWT_SECRET=0b1dd73601787df8dd1a6c6c8e9007bbf9d1251afab9910d771ed61908896446"
echo "Run: flyctl secrets set USE_FIXTURES=false"
echo ""
echo "Step 4: Deploy"
echo "Run: flyctl deploy"
echo ""
echo "Step 5: Check status"
echo "Run: flyctl status"
