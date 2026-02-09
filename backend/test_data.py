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

print("=== CATEGORIES ===")
cats = list(categories.find({}, {'_id': 0}))
for cat in cats:
    print(f"Category: {cat}")

print("\n=== PRODUCTS ===")  
prods = list(products.find({}, {'_id': 0}))
for prod in prods:
    print(f"Product: {prod}")

print("\n=== GROUPING TEST ===")
# Test the grouping logic like in frontend
groupedProducts = {}
for product in prods:
    if product['category_id'] not in groupedProducts:
        groupedProducts[product['category_id']] = []
    groupedProducts[product['category_id']].append(product)

print("Grouped products by category:")
for cat_id in groupedProducts:
    print(f"Category {cat_id}: {len(groupedProducts[cat_id])} products")
