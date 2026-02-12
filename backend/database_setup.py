from pymongo import MongoClient
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client['napling_choice_awards']

# Collections
categories = db['categories']
nominees = db['nominees']
votes = db['votes']
admin_users = db['admin_users']

def setup_database():
    """Initialize the database with sample data"""

    # Clear existing data (optional - remove this in production)
    categories.delete_many({})
    nominees.delete_many({})
    votes.delete_many({})
    admin_users.delete_many({})

    # Create sample categories
    sample_categories = [
        {
            'name': 'Best Picture',
            'description': 'Award for the most outstanding motion picture of the year',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Best Director',
            'description': 'Award for exceptional achievement in film direction',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Best Actor',
            'description': 'Award for outstanding performance by an actor in a leading role',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Best Actress',
            'description': 'Award for outstanding performance by an actress in a leading role',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Best Supporting Actor',
            'description': 'Award for outstanding performance by an actor in a supporting role',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Best Supporting Actress',
            'description': 'Award for outstanding performance by an actress in a supporting role',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Best Original Screenplay',
            'description': 'Award for the best original screenplay written directly for the screen',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Best Adapted Screenplay',
            'description': 'Award for the best screenplay adapted from previously existing material',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Best Cinematography',
            'description': 'Award for outstanding achievement in cinematography',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Best Original Score',
            'description': 'Award for the best original score created specifically for a film',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Best Original Song',
            'description': 'Award for the best original song written specifically for a film',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Best Production Design',
            'description': 'Award for outstanding achievement in production design',
            'created_at': datetime.datetime.now(datetime.UTC)
        }
    ]

    # Insert categories
    category_ids = []
    for category in sample_categories:
        result = categories.insert_one(category)
        category_id = str(result.inserted_id)
        # Update the document to include the id field
        categories.update_one(
            {'_id': result.inserted_id},
            {'$set': {'id': category_id}}
        )
        category_ids.append(category_id)
        print(f"Created category: {category['name']} with ID: {category_id}")
        # print(categories.find_one({'_id': result.inserted_id}))

    # Create sample nominees
    sample_nominees = [
        # Best Picture nominees
        {
            'name': 'Oppenheimer',
            'description': 'A biographical thriller about J. Robert Oppenheimer and the development of the atomic bomb',
            'category_id': category_ids[0],
            'image_url': 'https://via.placeholder.com/300x200/4b6460/ffffff?text=Oppenheimer',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Barbie',
            'description': 'A comedy film about the iconic doll who leaves Barbieland for the real world',
            'category_id': category_ids[0],
            'image_url': 'https://via.placeholder.com/300x200/edccbd/4b6460?text=Barbie',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Killers of the Flower Moon',
            'description': 'A historical crime drama about the Osage murders in the 1920s',
            'category_id': category_ids[0],
            'image_url': 'https://via.placeholder.com/300x200/7d9a86/ffffff?text=Killers+of+the+Flower+Moon',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'The Holdovers',
            'description': 'A comedy-drama about a teacher and students stuck at boarding school over Christmas',
            'category_id': category_ids[0],
            'image_url': 'https://via.placeholder.com/300x200/4b6460/ffffff?text=The+Holdovers',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Anatomy of a Fall',
            'description': 'A French legal drama about a woman accused of her husband\'s murder',
            'category_id': category_ids[0],
            'image_url': 'https://via.placeholder.com/300x200/edccbd/4b6460?text=Anatomy+of+a+Fall',
            'created_at': datetime.datetime.now(datetime.UTC)
        },

        # Best Director nominees
        {
            'name': 'Christopher Nolan',
            'description': 'For "Oppenheimer" - Masterful direction of a complex historical epic',
            'category_id': category_ids[1],
            'image_url': 'https://via.placeholder.com/300x200/7d9a86/ffffff?text=Christopher+Nolan',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Greta Gerwig',
            'description': 'For "Barbie" - Innovative direction of a cultural phenomenon',
            'category_id': category_ids[1],
            'image_url': 'https://via.placeholder.com/300x200/4b6460/ffffff?text=Greta+Gerwig',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Martin Scorsese',
            'description': 'For "Killers of the Flower Moon" - Epic storytelling at its finest',
            'category_id': category_ids[1],
            'image_url': 'https://via.placeholder.com/300x200/edccbd/4b6460?text=Martin+Scorsese',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Alexander Payne',
            'description': 'For "The Holdovers" - Heartwarming and nuanced direction',
            'category_id': category_ids[1],
            'image_url': 'https://via.placeholder.com/300x200/7d9a86/ffffff?text=Alexander+Payne',
            'created_at': datetime.datetime.now(datetime.UTC)
        },

        # Best Actor nominees
        {
            'name': 'Cillian Murphy',
            'description': 'For "Oppenheimer" - Transformative performance as the father of the atomic bomb',
            'category_id': category_ids[2],
            'image_url': 'https://via.placeholder.com/300x200/4b6460/ffffff?text=Cillian+Murphy',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Paul Giamatti',
            'description': 'For "The Holdovers" - Hilarious and heartbreaking as a curmudgeonly teacher',
            'category_id': category_ids[2],
            'image_url': 'https://via.placeholder.com/300x200/edccbd/4b6460?text=Paul+Giamatti',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Bradley Cooper',
            'description': 'For "Maestro" - Remarkable transformation as composer Leonard Bernstein',
            'category_id': category_ids[2],
            'image_url': 'https://via.placeholder.com/300x200/7d9a86/ffffff?text=Bradley+Cooper',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Jeffrey Wright',
            'description': 'For "American Fiction" - Brilliant performance as a frustrated novelist',
            'category_id': category_ids[2],
            'image_url': 'https://via.placeholder.com/300x200/4b6460/ffffff?text=Jeffrey+Wright',
            'created_at': datetime.datetime.now(datetime.UTC)
        },

        # Best Actress nominees
        {
            'name': 'Lily Gladstone',
            'description': 'For "Killers of the Flower Moon" - Powerful performance as an Osage woman',
            'category_id': category_ids[3],
            'image_url': 'https://via.placeholder.com/300x200/edccbd/4b6460?text=Lily+Gladstone',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Emma Stone',
            'description': 'For "Poor Things" - Daring and unforgettable performance',
            'category_id': category_ids[3],
            'image_url': 'https://via.placeholder.com/300x200/7d9a86/ffffff?text=Emma+Stone',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Sandra Hüller',
            'description': 'For "Anatomy of a Fall" - Complex and compelling courtroom drama performance',
            'category_id': category_ids[3],
            'image_url': 'https://via.placeholder.com/300x200/4b6460/ffffff?text=Sandra+Hüller',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Carey Mulligan',
            'description': 'For "Maestro" - Elegant and moving performance',
            'category_id': category_ids[3],
            'image_url': 'https://via.placeholder.com/300x200/edccbd/4b6460?text=Carey+Mulligan',
            'created_at': datetime.datetime.now(datetime.UTC)
        },

        # Best Supporting Actor nominees
        {
            'name': 'Robert De Niro',
            'description': 'For "Killers of the Flower Moon" - Menacing and nuanced performance',
            'category_id': category_ids[4],
            'image_url': 'https://via.placeholder.com/300x200/7d9a86/ffffff?text=Robert+De+Niro',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Robert Downey Jr.',
            'description': 'For "Oppenheimer" - Clever and complex performance as Lewis Strauss',
            'category_id': category_ids[4],
            'image_url': 'https://via.placeholder.com/300x200/4b6460/ffffff?text=Robert+Downey+Jr.',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Ryan Gosling',
            'description': 'For "Barbie" - Hilarious and scene-stealing as Ken',
            'category_id': category_ids[4],
            'image_url': 'https://via.placeholder.com/300x200/edccbd/4b6460?text=Ryan+Gosling',
            'created_at': datetime.datetime.now(datetime.UTC)
        },

        # Best Supporting Actress nominees
        {
            'name': 'Da\'Vine Joy Randolph',
            'description': 'For "The Holdovers" - Heartbreaking and humorous as a grieving cook',
            'category_id': category_ids[5],
            'image_url': 'https://via.placeholder.com/300x200/7d9a86/ffffff?text=Da\'Vine+Joy+Randolph',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Emily Blunt',
            'description': 'For "Oppenheimer" - Compelling performance as an alcoholic scientist',
            'category_id': category_ids[5],
            'image_url': 'https://via.placeholder.com/300x200/4b6460/ffffff?text=Emily+Blunt',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'America Ferrera',
            'description': 'For "Barbie" - Powerful monologue about womanhood',
            'category_id': category_ids[5],
            'image_url': 'https://via.placeholder.com/300x200/edccbd/4b6460?text=America+Ferrera',
            'created_at': datetime.datetime.now(datetime.UTC)
        },

        # Best Original Screenplay nominees
        {
            'name': 'The Holdovers',
            'description': 'Written by David Hemingson - Charming and original screenplay',
            'category_id': category_ids[6],
            'image_url': 'https://via.placeholder.com/300x200/7d9a86/ffffff?text=The+Holdovers',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Anatomy of a Fall',
            'description': 'Written by Justine Triet & Arthur Harari - Intriguing legal drama',
            'category_id': category_ids[6],
            'image_url': 'https://via.placeholder.com/300x200/4b6460/ffffff?text=Anatomy+of+a+Fall',
            'created_at': datetime.datetime.now(datetime.UTC)
        },

        # Best Adapted Screenplay nominees
        {
            'name': 'Oppenheimer',
            'description': 'Written by Christopher Nolan - Adapted from "American Prometheus"',
            'category_id': category_ids[7],
            'image_url': 'https://via.placeholder.com/300x200/edccbd/4b6460?text=Oppenheimer',
            'created_at': datetime.datetime.now(datetime.UTC)
        },
        {
            'name': 'Barbie',
            'description': 'Written by Greta Gerwig & Noah Baumbach - Based on Mattel dolls',
            'category_id': category_ids[7],
            'image_url': 'https://via.placeholder.com/300x200/7d9a86/ffffff?text=Barbie',
            'created_at': datetime.datetime.now(datetime.UTC)
        }
    ]

    # Insert nominees
    for nominee in sample_nominees:
        result = nominees.insert_one(nominee)
        nominee_id = str(result.inserted_id)
        # Update the document to include the id field
        nominees.update_one(
            {'_id': result.inserted_id},
            {'$set': {'id': nominee_id}}
        )
        print(f"Created nominee: {nominee['name']} with ID: {nominee_id}")
        print(nominees.find_one({'_id': result.inserted_id}))

    # Create indexes for better performance
    votes.create_index([("category_id", 1), ("voter_ip", 1)], unique=True)
    nominees.create_index([("category_id", 1)])
    categories.create_index([("name", 1)], unique=True)

    print("\nDatabase setup completed successfully!")
    print(f"Created {len(category_ids)} award categories and {len(sample_nominees)} nominees")
    print("Indexes created for optimal performance")

if __name__ == "__main__":
    setup_database()
