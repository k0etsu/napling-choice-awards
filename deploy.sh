#!/bin/bash

# Deployment script for Napling Choice Awards
echo "🚀 Starting deployment process..."

# Navigate to project root
cd "$(dirname "$0")"

# Build the frontend
echo "📦 Building frontend..."
cd frontend
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Frontend build successful"
else
    echo "❌ Frontend build failed"
    exit 1
fi

# Go back to project root
cd ..

# Create uploads directory in build folder if it doesn't exist
mkdir -p frontend/build/uploads

echo "📁 Uploads directory created/verified in build folder"

echo "🎉 Deployment ready!"
echo "📋 Next steps:"
echo "   1. Run the backend: cd backend && python app.py"
echo "   2. The app will be available at: http://localhost:5001"
echo "   3. Uploaded images will be stored in: frontend/build/uploads/"
echo "   4. Images will be accessible at: http://localhost:5001/uploads/[filename]"
