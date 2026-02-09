# Running Backend with UV

## Prerequisites
- Install UV: `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Setup
1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies with UV:
   ```bash
   uv sync
   ```

3. Copy environment file:
   ```bash
   cp .env.example .env
   ```

4. Update .env with your MongoDB URI

## Running the App

### Development
```bash
uv run python app.py
```

### Production with Gunicorn
```bash
uv run gunicorn app:app --host 0.0.0.0 --port 5000
```

## Database Setup
```bash
uv run python database_setup.py
```

## Benefits of UV
- Faster dependency resolution
- Better caching
- Lockfile management
- Reproducible environments
