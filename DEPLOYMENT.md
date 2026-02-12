# Deployment Guide

## Overview
The Napling Choice Awards application has been updated for proper deployment with image accessibility.

## Changes Made

### Backend Updates (`backend/app.py`)
- **Upload Folder**: Changed from `'uploads'` to `frontend/build/uploads`
- **Static File Serving**: Added routes to serve React static files from `frontend/build/static`
- **Catch-all Route**: Added route to serve React app for all non-API routes
- **Image Access**: Images accessible via `/uploads/[filename]` when deployed

### Frontend Updates
- **Image URL Handling**: Updated all components to use `/uploads/[filename]` instead of hardcoded localhost URLs
- **Utility Functions**: Added `getImageUrl()` utility function for consistent image URL construction
- **Components Updated**: Home.js, Admin.js, and Results.js all use the new image URL pattern

## Deployment Structure
```
frontend/
├── build/
│   ├── static/     # React static assets
│   ├── uploads/     # User uploaded images
│   └── index.html   # React app entry point
└── src/
```

## Route Structure
- `/api/*` - Backend API routes
- `/uploads/*` - User uploaded images
- `/static/*` - React static files
- `/*` - React app (catch-all)

## Deployment Steps

1. **Build Frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Run Backend**
   ```bash
   cd backend
   python app.py
   ```

3. **Access Application**
   - Main app: `http://localhost:5001`
   - API: `http://localhost:5001/api/*`
   - Images: `http://localhost:5001/uploads/[filename]`

## Automated Deployment
Use the provided deployment script:
```bash
chmod +x deploy.sh
./deploy.sh
```

The deployment script will:
- Build the React frontend
- Create uploads directory in build folder
- Provide clear deployment instructions

## Image URL Handling

All components now use a consistent `getImageUrl()` utility function:
```javascript
const getImageUrl = (image_url) => {
  if (!image_url) return '';
  return image_url.startsWith('http') ? image_url : `/uploads/${image_url.split('/').pop()}`;
};
```

This ensures:
- External URLs (http/https) are used as-is
- Local uploads are properly constructed with `/uploads/` prefix
- Consistent behavior across all components

## Image Removal Functionality

### Backend Implementation
The backend properly handles image deletion when nominees are modified:

**1. Individual Image Removal** (`/api/nominees/<nominee_id>/image`):
- Removes image file from `frontend/build/uploads/` directory
- Updates nominee record to remove `image_url` field
- Maintains nominee record (only removes image)

**2. Complete Nominee Deletion** (`/api/nominees/<nominee_id>`):
- Removes nominee record and all associated votes
- Automatically deletes associated image file
- Cleans up orphaned images

### Frontend Implementation
**Admin.js Component:**
- Added `handleRemoveImage()` function to call backend API
- "Remove Image" button now properly calls `/api/nominees/{id}/image`
- Updates local state and shows success/error messages
- Maintains data consistency between frontend and backend

**Image Management Logic:**
- **Temporary Images**: Stored in state until user commits changes
- **Old Image Cleanup**: Automatically deletes previous image when new one is uploaded
- **Explicit Removal**: Individual image removal via "Remove Image" button
- **Robust Error Handling**: Proper feedback for all image operations

**Image Cleanup Process:**
```javascript
// Store original image URL for potential cleanup
const originalImageUrl = editingNominee.image_url;

// Upload new image and update nominee
await axios.post('/api/nominees', nomineeData);

// Clean up old image if new one was uploaded
if (originalImageUrl && originalImageUrl !== nomineeData.image_url && originalImageUrl.startsWith('/uploads/')) {
  const oldFilename = originalImageUrl.replace('/uploads/', '');
  await axios.delete(`/api/nominees/${editingNominee.id}/image?filename=${oldFilename}`);
  console.log('Cleaned up old image:', oldFilename);
}
