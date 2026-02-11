from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
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

# Configure CORS with specific origins
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, origins=allowed_origins, methods=['GET', 'POST', 'PUT', 'DELETE'])

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[f"{os.getenv('RATE_LIMIT_PER_MINUTE', '60')}/minute"]
)

# Configure caching
config = {
    "CACHE_TYPE": "SimpleCache",  # Use RedisCache for production
    "CACHE_DEFAULT_TIMEOUT": 300,  # 5 minutes default
    "CACHE_THRESHOLD": 1000,  # Max number of cached items
}
app.config.from_mapping(config)
cache = Cache(app)

# Upload configuration
UPLOAD_FOLDER = 'uploads'
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
products = db['products']
votes = db['votes']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

def validate_product_data(data):
    """Validate product input data"""
    errors = []

    if not data.get('name') or len(data.get('name', '').strip()) < 1:
        errors.append('Product name is required')
    elif len(data.get('name', '').strip()) > 100:
        errors.append('Product name must be less than 100 characters')

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

@app.route('/api/upload', methods=['POST'])
@limiter.limit("10/minute")
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

@app.route('/api/products', methods=['GET'])
@cache.cached(timeout=300, query_string=True)  # Cache for 5 minutes
def get_products():
    category_id = request.args.get('category_id')
    query = {}
    if category_id:
        query['category_id'] = category_id

    prods = list(products.find(query, {'_id': 0}))
    # Convert ObjectId to string id for each product
    # for prod in prods:
    #     prod['id'] = str(prod.pop('_id', ''))
    return prods

@app.route('/api/products', methods=['POST'])
@limiter.limit("20/minute")
def create_product():
    data = request.get_json()

    # Validate input
    errors = validate_product_data(data)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    product = {
        'name': sanitize_input(data['name']),
        'description': sanitize_input(data.get('description', '')),
        'category_id': data['category_id'],
        'image_url': data.get('image_url', ''),
        'youtube_url': data.get('youtube_url', ''),
        'created_at': datetime.datetime.now(datetime.UTC)
    }
    result = products.insert_one(product)
    product['id'] = str(result.inserted_id)
    # Update the document to include the id field
    products.update_one(
        {'_id': result.inserted_id},
        {'$set': {'id': str(result.inserted_id)}}
    )

    # Clear relevant caches
    cache.clear()  # Clear all cache when products change

    return json.loads(json_util.dumps(product)), 201

@app.route('/api/categories/<category_id>', methods=['PUT'])
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

@app.route('/api/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.get_json()

        # Check if product exists
        product = products.find_one({'_id': ObjectId(product_id)})
        if not product:
            return {'error': 'Product not found'}, 404

        # Update product
        update_data = {
            'name': data.get('name', product['name']),
            'description': data.get('description', product['description']),
            'category_id': data.get('category_id', product['category_id']),
            'image_url': data.get('image_url', product.get('image_url', '')),
            'youtube_url': data.get('youtube_url', product.get('youtube_url', '')),
            'updated_at': datetime.datetime.now(datetime.UTC)
        }

        result = products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': update_data}
        )

        if result.modified_count > 0:
            # Clear relevant caches
            cache.clear()  # Clear all cache when products change

            # Return updated product
            updated_product = products.find_one({'_id': ObjectId(product_id)}, {'_id': 0})
            return json.loads(json_util.dumps(updated_product)), 200
        else:
            return {'error': 'No changes made to product'}, 400

    except Exception as e:
        print(f"Error updating product {product_id}: {str(e)}")
        return {'error': 'Failed to update product'}, 500

@app.route('/api/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    try:
        # First check if category exists
        category = categories.find_one({'_id': ObjectId(category_id)})
        if not category:
            return {'error': 'Category not found'}, 404

        # Count products to be deleted for logging
        products_to_delete = list(products.find({'category_id': category_id}))
        products_count = len(products_to_delete)

        # Delete the category
        result = categories.delete_one({'_id': ObjectId(category_id)})

        # Delete all products associated with this category
        products_result = products.delete_many({'category_id': category_id})

        # Delete all votes for products in this category
        votes_result = votes.delete_many({'category_id': category_id})

        if result.deleted_count > 0:
            # Clear relevant caches
            cache.clear()  # Clear all cache when categories change

            return {
                'message': f'Category "{category["name"]}" deleted successfully',
                'deleted_products': products_count,
                'products_deleted': products_result.deleted_count if hasattr(products_result, 'deleted_count') else 0
            }, 200
        else:
            return {'error': 'Failed to delete category'}, 500

    except Exception as e:
        print(f"Error deleting category {category_id}: {str(e)}")
        return {'error': 'Failed to delete category'}, 500

@app.route('/api/products/<product_id>/image', methods=['DELETE'])
def remove_product_image(product_id):
    try:
        # Get product details
        product = products.find_one({'_id': ObjectId(product_id)})
        if not product:
            return {'error': 'Product not found'}, 404

        # Delete associated image file if it exists
        image_url = product.get('image_url', '')
        if image_url and image_url.startswith('/uploads/'):
            filename = image_url.replace('/uploads/', '')
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"Deleted image file: {image_path}")
            except Exception as e:
                print(f"Error deleting image file {image_path}: {str(e)}")
                # Continue with product update even if image deletion fails

        # Update product to remove image_url
        result = products.update_one(
            {'_id': ObjectId(product_id)},
            {'$unset': {'image_url': 1}}
        )

        if result.modified_count > 0:
            return {'success': 'Image removed successfully'}, 200
        else:
            return {'error': 'Failed to remove image'}, 500

    except Exception as e:
        print(f"Error removing product image: {str(e)}")
        return {'error': 'Failed to remove image'}, 500

@app.route('/api/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        # Get product details before deletion to retrieve image_url
        product = products.find_one({'_id': ObjectId(product_id)})
        if not product:
            return {'error': 'Product not found'}, 404

        # Delete associated image file if it exists
        image_url = product.get('image_url', '')
        if image_url and image_url.startswith('/uploads/'):
            filename = image_url.replace('/uploads/', '')
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"Deleted image file: {image_path}")
            except Exception as e:
                print(f"Error deleting image file {image_path}: {str(e)}")
                # Continue with product deletion even if image deletion fails

        result = products.delete_one({'_id': ObjectId(product_id)})

        # Delete all votes for this product
        votes.delete_many({'product_id': product_id})

        if result.deleted_count > 0:
            # Clear relevant caches
            cache.clear()  # Clear all cache when products change

            return {'message': 'Product deleted successfully'}, 200
        else:
            return {'error': 'Product not found'}, 404
    except Exception as e:
        return {'error': 'Failed to delete product'}, 500

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
        'voter_ip': request.remote_addr
    })

    vote_data = {
        'product_id': data['product_id'],
        'category_id': data['category_id'],
        'voter_ip': request.remote_addr,
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
        'voter_ip': request.remote_addr
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
            '_id': '$product_id',
            'vote_count': {'$sum': 1}
        }},
        {'$sort': {'vote_count': -1}}
    ]

    results = list(votes.aggregate(pipeline))

    # Get product details
    for result in results:
        product = products.find_one({'id': result['_id']}, {'_id': 0})
        result['product'] = product
        result['product_id'] = result['_id']
        del result['_id']

    return results

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
