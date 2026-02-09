# Napling Choice Awards

A modern voting platform for Nimi Nightmare's annual award show. Built with React, Flask, and MongoDB.

## Features

- **Modern, Clean Design**: Beautiful UI with custom color palette (#4b6460, #edccbd, #7d9a86)
- **Napling Choice Awards Nominee Showcase**: Display nominees for each award category
- **Voting System**: Users can vote once per category (IP-based restriction)
- **Admin Panel**: Manage award categories and nominees through an intuitive interface
- **Results Viewing**: View voting results with ranking and vote counts
- **Responsive Design**: Works seamlessly on all devices
- **Accessible**: Built with accessibility best practices

## Technology Stack

### Frontend
- React 18.2.0
- React Router DOM 6.8.0
- Bootstrap 5.2.3
- React Bootstrap 2.10.0
- Axios 1.3.2

### Backend
- Flask 3.0.3 (Python 3.12+)
- Flask-CORS 4.0.0
- Flask-Limiter 3.5.0
- Flask-Caching 2.1.0
- PyMongo 4.3.3
- Gunicorn 20.1.0

### Database
- MongoDB for storing categories, nominees, and votes

## Project Structure

```
napling-choice-awards/
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Admin.js
│   │   │   ├── Home.js
│   │   │   ├── Results.js
│   │   │   ├── VideoModal.js
│   │   │   ├── Home.css
│   │   │   └── Results.css
│   │   ├── contexts/
│   │   ├── utils/
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json
│   └── package-lock.json
├── backend/
│   ├── uploads/
│   ├── app.py
│   ├── database_setup.py
│   ├── test_data.py
│   ├── fix_ids.py
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── .env.example
│   └── README_UV.md
├── deployment/
│   ├── deploy.sh
│   ├── gunicorn.service
│   └── nginx.conf
├── .gitignore
├── README.md
├── instructions.md
└── napling-choice-awards.code-workspace
```

## Installation & Setup

### Prerequisites
- Node.js 16+ and npm
- Python 3.12+
- MongoDB
- uv (recommended for Python package management)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your MongoDB connection string and other settings
```

4. Initialize the database:
```bash
python database_setup.py
```

5. Run the development server:
```bash
uv run flask run
# or
python app.py
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:3000` with the backend API at `http://localhost:5000`.

## Usage

### For Voters
- Visit the home page to view all award categories and nominees
- Cast your vote in each category (one vote per category per IP)
- View real-time results on the Results page

### For Administrators
- Access the Admin panel to manage categories and nominees
- Add/edit/delete award categories
- Add/edit/delete nominees with images and descriptions

## API Endpoints

- `GET /api/categories` - Get all award categories
- `GET /api/nominees` - Get all nominees
- `POST /api/vote` - Submit a vote
- `GET /api/results` - Get voting results
- `POST /api/admin/category` - Add new category (admin)
- `POST /api/admin/nominee` - Add new nominee (admin)

## Deployment

The `deployment/` directory contains configuration files for production deployment:
- `nginx.conf` - Nginx configuration
- `gunicorn.service` - Systemd service for Gunicorn
- `deploy.sh` - Deployment script

## Security Features

- IP-based voting restrictions
- Rate limiting on API endpoints
- CORS protection
- Input validation and sanitization
- Secure file upload handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.
