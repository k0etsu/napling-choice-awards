from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client['napling_choice_awards']

# Collections
categories = db['categories']
products = db['products']

print("Fixing category IDs...")
cats = list(categories.find({}))
for cat in cats:
    if '_id' in cat and 'id' not in cat:
        cat_id = str(cat['_id'])
        categories.update_one(
            {'_id': cat['_id']},
            {'$set': {'id': cat_id}}
        )
        print(f"Updated category {cat.get('name', 'Unknown')} with ID: {cat_id}")

print("\nFixing product IDs...")
prods = list(products.find({}))
for prod in prods:
    if '_id' in prod and 'id' not in prod:
        prod_id = str(prod['_id'])
        products.update_one(
            {'_id': prod['_id']},
            {'$set': {'id': prod_id}}
        )
        print(f"Updated product {prod.get('name', 'Unknown')} with ID: {prod_id}")

print("\nID fixing completed!")
