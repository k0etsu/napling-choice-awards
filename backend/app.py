from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import datetime
from bson import json_util, ObjectId
import json
import re
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=24)

# Initialize JWT
jwt = JWTManager(app)

# Configure CORS with specific origins
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, origins=allowed_origins, methods=['GET', 'POST', 'PUT', 'DELETE'])

# Configure caching
config = {
    "CACHE_TYPE": "SimpleCache",  # Use RedisCache for production
    "CACHE_DEFAULT_TIMEOUT": 300,  # 5 minutes default
    "CACHE_THRESHOLD": 1000,  # Max number of cached items
}
app.config.from_mapping(config)
cache = Cache(app)

# Upload configuration - place uploads in frontend build directory for deployment
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'build', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MongoDB connection with security
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
ssl_enabled = os.getenv('MONGODB_SSL', 'false').lower() == 'true'

# Build connection kwargs dynamically
connection_kwargs = {
    'authSource': os.getenv('MONGODB_AUTH_SOURCE', 'admin'),
    'connectTimeoutMS': 5000,
    'serverSelectionTimeoutMS': 5000
}

# Only add SSL/TLS options if SSL is enabled
if ssl_enabled:
    connection_kwargs.update({
        'ssl': True,
        'tlsAllowInvalidCertificates': False
    })

client = MongoClient(MONGODB_URI, **connection_kwargs)
db = client['napling_choice_awards']

# Collections
categories = db['categories']
nominees = db['nominees']
votes = db['votes']
admin_users = db['admin_users']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_client_ip():
    """Get the real client IP address, accounting for proxies"""
    # Check for X-Forwarded-For header (set by nginx/proxy)
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For can contain multiple IPs, take the first one (original client)
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()

    # Check for X-Real-IP header (also set by nginx)
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP').strip()

    # Fall back to remote_addr (direct connection)
    return request.remote_addr

# Rate limiting
def get_rate_limit_key():
    """Get the proper key for rate limiting based on real client IP"""
    return get_client_ip()

limiter = Limiter(
    app=app,
    key_func=get_rate_limit_key,
    default_limits=[f"{os.getenv('RATE_LIMIT_PER_MINUTE', '60')}/minute"]
)

def validate_object_id(id_string):
    """Validate MongoDB ObjectId format"""
    try:
        ObjectId(id_string)
        return True
    except:
        return False

def sanitize_input(text):
    """Basic input sanitization"""
    if not isinstance(text, str):
        return text
    # Remove potentially dangerous characters
    return re.sub(r'[<>"\']', '', text.strip())

def validate_category_data(data):
    """Validate category input data"""
    errors = []

    if not data.get('name') or len(data.get('name', '').strip()) < 1:
        errors.append('Category name is required')
    elif len(data.get('name', '').strip()) > 100:
        errors.append('Category name must be less than 100 characters')

    description = data.get('description', '')
    if len(description) > 500:
        errors.append('Description must be less than 500 characters')

    return errors

def validate_nominee_data(data):
    """Validate nominee input data"""
    errors = []

    if not data.get('name') or len(data.get('name', '').strip()) < 1:
        errors.append('Nominee name is required')
    elif len(data.get('name', '').strip()) > 100:
        errors.append('Nominee name must be less than 100 characters')

    if not data.get('category_id') or not validate_object_id(data['category_id']):
        errors.append('Valid category ID is required')

    description = data.get('description', '')
    if len(description) > 1000:
        errors.append('Description must be less than 1000 characters')

    # Validate URLs if provided
    for url_field in ['image_url', 'youtube_url']:
        url = data.get(url_field, '')
        if url and not re.match(r'^https?://', url):
            errors.append(f'{url_field.replace("_", " ").title()} must be a valid URL')

    return errors

# Initialize default admin users
def initialize_admin_users():
    """Create default admin users if they don't exist"""
    default_admins = [
        {'username': 'admin', 'password': os.getenv('ADMIN_PASSWORD', 'admin123')},
        {'username': 'nimi', 'password': os.getenv('NIMI_PASSWORD', 'nimi123')}
    ]

    for admin_data in default_admins:
        existing_admin = admin_users.find_one({'username': admin_data['username']})
        if not existing_admin:
            hashed_password = generate_password_hash(admin_data['password'])
            admin_user = {
                'username': admin_data['username'],
                'password': hashed_password,
                'created_at': datetime.datetime.now(datetime.UTC),
                'role': 'admin'
            }
            admin_users.insert_one(admin_user)
            print(f"Created default admin user: {admin_data['username']}")

# Initialize admin users on startup
initialize_admin_users()

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10/minute")
def login():
    """Admin login endpoint"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400

    username = data['username'].strip()
    password = data['password']

    # Find admin user
    admin_user = admin_users.find_one({'username': username})

    if not admin_user or not check_password_hash(admin_user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Create access token
    access_token = create_access_token(identity=username)

    return jsonify({
        'access_token': access_token,
        'username': username,
        'message': 'Login successful'
    }), 200

@app.route('/api/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password for authenticated admin"""
    current_user = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current password and new password are required'}), 400

    current_password = data['current_password']
    new_password = data['new_password']

    # Validate new password length
    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters long'}), 400

    # Get current user
    admin_user = admin_users.find_one({'username': current_user})

    if not admin_user or not check_password_hash(admin_user['password'], current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401

    # Update password
    hashed_new_password = generate_password_hash(new_password)
    admin_users.update_one(
        {'username': current_user},
        {'$set': {
            'password': hashed_new_password,
            'password_changed_at': datetime.datetime.now(datetime.UTC)
        }}
    )

    return jsonify({'message': 'Password changed successfully'}), 200

@app.route('/api/auth/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token is valid"""
    current_user = get_jwt_identity()
    return jsonify({'username': current_user, 'valid': True}), 200

@app.route('/api/upload', methods=['POST'])
@limiter.limit("10/minute")
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid filename conflicts
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Return the URL that can be used to access the file
        file_url = f"/uploads/{filename}"
        return jsonify({'filename': filename, 'url': file_url}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Serve React static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'build', 'static')
    return send_from_directory(static_dir, filename)

@app.route('/api/categories', methods=['GET'])
@cache.cached(timeout=600)  # Cache for 10 minutes
def get_categories():
    cats = list(categories.find({}, {'_id': 0}))
    # Convert ObjectId to string id for each category
    # for cat in cats:
    #     cat['id'] = str(cat.pop('_id', ''))
    return cats

@app.route('/api/categories', methods=['POST'])
@limiter.limit("20/minute")
@jwt_required()
def create_category():
    data = request.get_json()

    # Validate input
    errors = validate_category_data(data)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    category = {
        'name': sanitize_input(data['name']),
        'description': sanitize_input(data.get('description', '')),
        'voting_locked': data.get('voting_locked', False),
        'created_at': datetime.datetime.now(datetime.UTC)
    }
    result = categories.insert_one(category)
    category['id'] = str(result.inserted_id)
    # Update the document to include the id field
    categories.update_one(
        {'_id': result.inserted_id},
        {'$set': {'id': str(result.inserted_id)}}
    )

    # Clear relevant caches
    cache.clear()  # Clear all cache when categories change

    return json.loads(json_util.dumps(category)), 201

@app.route('/api/nominees', methods=['GET'])
@cache.cached(timeout=300, query_string=True)  # Cache for 5 minutes
def get_nominees():
    category_id = request.args.get('category_id')
    query = {}
    if category_id:
        query['category_id'] = category_id

    prods = list(nominees.find(query, {'_id': 0}))
    # Convert ObjectId to string id for each nominee
    # for prod in prods:
    #     prod['id'] = str(prod.pop('_id', ''))
    return prods

@app.route('/api/nominees', methods=['POST'])
@limiter.limit("20/minute")
@jwt_required()
def create_nominee():
    data = request.get_json()

    # Validate input
    errors = validate_nominee_data(data)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    nominee = {
        'name': sanitize_input(data['name']),
        'description': sanitize_input(data.get('description', '')),
        'category_id': data['category_id'],
        'image_url': data.get('image_url', ''),
        'youtube_url': data.get('youtube_url', ''),
        'created_at': datetime.datetime.now(datetime.UTC)
    }
    result = nominees.insert_one(nominee)
    nominee['id'] = str(result.inserted_id)
    # Update the document to include the id field
    nominees.update_one(
        {'_id': result.inserted_id},
        {'$set': {'id': str(result.inserted_id)}}
    )

    # Clear relevant caches
    cache.clear()  # Clear all cache when nominees change
    return json.loads(json_util.dumps(nominee)), 201

@app.route('/api/categories/<category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    try:
        data = request.get_json()

        # Check if category exists
        category = categories.find_one({'_id': ObjectId(category_id)})
        if not category:
            return {'error': 'Category not found'}, 404

        # Update category
        update_data = {
            'name': data.get('name', category['name']),
            'description': data.get('description', category['description']),
            'voting_locked': data.get('voting_locked', category.get('voting_locked', False)),
            'updated_at': datetime.datetime.now(datetime.UTC)
        }

        result = categories.update_one(
            {'_id': ObjectId(category_id)},
            {'$set': update_data}
        )

        if result.modified_count > 0:
            # Clear relevant caches
            cache.clear()  # Clear all cache when categories change

            # Return updated category
            updated_category = categories.find_one({'_id': ObjectId(category_id)}, {'_id': 0})
            return json.loads(json_util.dumps(updated_category)), 200
        else:
            return {'error': 'No changes made to category'}, 400

    except Exception as e:
        print(f"Error updating category {category_id}: {str(e)}")
        return {'error': 'Failed to update category'}, 500

@app.route('/api/nominees/<nominee_id>', methods=['PUT'])
@jwt_required()
def update_nominee(nominee_id):
    try:
        data = request.get_json()

        # Check if nominee exists
        nominee = nominees.find_one({'_id': ObjectId(nominee_id)})
        if not nominee:
            return {'error': 'Nominee not found'}, 404

        # Update nominee
        update_data = {
            'name': data.get('name', nominee['name']),
            'description': data.get('description', nominee['description']),
            'category_id': data.get('category_id', nominee['category_id']),
            'image_url': data.get('image_url', nominee.get('image_url', '')),
            'youtube_url': data.get('youtube_url', nominee.get('youtube_url', '')),
            'updated_at': datetime.datetime.now(datetime.UTC)
        }

        result = nominees.update_one(
            {'_id': ObjectId(nominee_id)},
            {'$set': update_data}
        )

        if result.modified_count > 0:
            # Clear relevant caches
            cache.clear()  # Clear all cache when nominees change

            # Return updated nominee
            updated_nominee = nominees.find_one({'_id': ObjectId(nominee_id)}, {'_id': 0})
            return json.loads(json_util.dumps(updated_nominee)), 200
        else:
            return {'error': 'No changes made to nominee'}, 400

    except Exception as e:
        print(f"Error updating nominee {nominee_id}: {str(e)}")
        return {'error': 'Failed to update nominee'}, 500

@app.route('/api/categories/<category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    try:
        # First check if category exists
        category = categories.find_one({'_id': ObjectId(category_id)})
        if not category:
            return {'error': 'Category not found'}, 404

        # Delete the category
        result = categories.delete_one({'_id': ObjectId(category_id)})

        # Delete all nominees for this category
        nominees_result = nominees.delete_many({'category_id': category_id})

        # Delete all votes for nominees in this category
        votes_result = votes.delete_many({'category_id': category_id})

        if result.deleted_count > 0:
            # Clear relevant caches
            cache.clear()  # Clear all cache when categories change

            return {
                'message': f'Category "{category["name"]}" deleted successfully',
                'deleted_nominees': nominees_result.deleted_count if hasattr(nominees_result, 'deleted_count') else 0,
                'nominees_deleted': nominees_result.deleted_count if hasattr(nominees_result, 'deleted_count') else 0
            }, 200
        else:
            return {'error': 'Failed to delete category'}, 500

    except Exception as e:
        print(f"Error deleting category {category_id}: {str(e)}")
        return {'error': 'Failed to delete category'}, 500

@app.route('/api/nominees/<nominee_id>/image', methods=['DELETE'])
@jwt_required()
def remove_nominee_image(nominee_id):
    try:
        # Get nominee details
        nominee = nominees.find_one({'_id': ObjectId(nominee_id)})
        if not nominee:
            return {'error': 'Nominee not found'}, 404

        # Delete associated image file if it exists
        image_url = nominee.get('image_url', '')
        if image_url and image_url.startswith('/uploads/'):
            filename = image_url.replace('/uploads/', '')
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"Deleted image file: {image_path}")
            except Exception as e:
                print(f"Error deleting image file {image_path}: {str(e)}")
                # Continue with nominee update even if image deletion fails

        # Update nominee to remove image_url
        result = nominees.update_one(
            {'_id': ObjectId(nominee_id)},
            {'$unset': {'image_url': 1}}
        )

        if result.modified_count > 0:
            return {'success': 'Image removed successfully'}, 200
        else:
            return {'error': 'Failed to remove image'}, 500

    except Exception as e:
        print(f"Error removing nominee image: {str(e)}")
        return {'error': 'Failed to remove image'}, 500

@app.route('/api/nominees/<nominee_id>', methods=['DELETE'])
@jwt_required()
def delete_nominee(nominee_id):
    try:
        # Get nominee details before deletion to retrieve image_url
        nominee = nominees.find_one({'_id': ObjectId(nominee_id)})
        if not nominee:
            return {'error': 'Nominee not found'}, 404

        # Delete associated image file if it exists
        image_url = nominee.get('image_url', '')
        if image_url and image_url.startswith('/uploads/'):
            filename = image_url.replace('/uploads/', '')
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"Deleted image file: {image_path}")
            except Exception as e:
                print(f"Error deleting image file {image_path}: {str(e)}")
                # Continue with nominee deletion even if image deletion fails

        result = nominees.delete_one({'_id': ObjectId(nominee_id)})

        # Delete all votes for this nominee
        votes.delete_many({'nominee_id': nominee_id})

        if result.deleted_count > 0:
            # Clear relevant caches
            cache.clear()  # Clear all cache when nominees change

            return {'message': 'Nominee deleted successfully'}, 200
        else:
            return {'error': 'Nominee not found'}, 404
    except Exception as e:
        return {'error': f'Failed to delete nominee {e}'}, 500

@app.route('/api/vote', methods=['POST'])
@limiter.limit("10/minute")
def cast_vote():
    data = request.get_json()

    # Check if category exists and voting is not locked
    category = categories.find_one({'id': data['category_id']})
    if not category:
        return {'error': 'Category not found'}, 404

    if category.get('voting_locked', False):
        return {'error': 'Voting is locked for this category'}, 403

    # Check for existing vote by this IP
    existing_vote = votes.find_one({
        'category_id': data['category_id'],
        'voter_ip': get_client_ip()
    })

    vote_data = {
        'nominee_id': data['nominee_id'],
        'category_id': data['category_id'],
        'voter_ip': get_client_ip(),
        'created_at': datetime.datetime.now(datetime.UTC)
    }

    if existing_vote:
        # Update existing vote
        votes.update_one(
            {'_id': existing_vote['_id']},
            {'$set': vote_data}
        )
        vote_data['id'] = str(existing_vote['_id'])
        vote_data['action'] = 'updated'
    else:
        # Create new vote
        result = votes.insert_one(vote_data)
        vote_data['id'] = str(result.inserted_id)
        vote_data['action'] = 'created'

    # Clear results cache for this category
    cache.clear()  # Clear all cache when votes change

    return json.loads(json_util.dumps(vote_data)), 201

@app.route('/api/vote/<category_id>', methods=['GET'])
@limiter.limit("240/minute")  # More lenient for vote checking
def get_user_vote(category_id):
    # Get user's current vote for this category
    existing_vote = votes.find_one({
        'category_id': category_id,
        'voter_ip': get_client_ip()
    }, {'_id': 0})

    if existing_vote:
        return json.loads(json_util.dumps(existing_vote)), 200
    else:
        return {'vote': None}, 200

@app.route('/api/results/<category_id>', methods=['GET'])
@cache.cached(timeout=60, query_string=True)  # Cache for 1 minute
def get_results(category_id):
    pipeline = [
        {'$match': {'category_id': category_id}},
        {'$group': {
            '_id': '$nominee_id',
            'vote_count': {'$sum': 1}
        }},
        {'$sort': {'vote_count': -1}}
    ]

    results = list(votes.aggregate(pipeline))

    # Get nominee details
    for result in results:
        nominee = nominees.find_one({'id': result['_id']}, {'_id': 0})
        result['nominee'] = nominee
        result['nominee_id'] = result['_id']
        del result['_id']

    return results

# Serve React app for all non-API routes (catch-all)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    build_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'build')
    if path != "" and os.path.exists(os.path.join(build_dir, path)):
        return send_from_directory(build_dir, path)
    else:
        return send_from_directory(build_dir, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
