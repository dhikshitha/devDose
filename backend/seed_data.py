#!/usr/bin/env python
from app import create_app, db
from models import Category, Tag, Concept, User
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_categories():
    """Seed initial categories"""
    categories = [
        {
            'name': 'Web Development',
            'description': 'Frontend and backend web technologies',
            'icon': '🌐'
        },
        {
            'name': 'Machine Learning',
            'description': 'AI, ML, and data science concepts',
            'icon': '🤖'
        },
        {
            'name': 'Cloud Computing',
            'description': 'Cloud platforms and services',
            'icon': '☁️'
        },
        {
            'name': 'DevOps',
            'description': 'Development operations and CI/CD',
            'icon': '🔧'
        },
        {
            'name': 'Cybersecurity',
            'description': 'Security concepts and best practices',
            'icon': '🔒'
        },
        {
            'name': 'Mobile Development',
            'description': 'iOS, Android, and cross-platform development',
            'icon': '📱'
        },
        {
            'name': 'Data Engineering',
            'description': 'Big data and data pipeline concepts',
            'icon': '📊'
        },
        {
            'name': 'Programming Languages',
            'description': 'Language-specific concepts and features',
            'icon': '💻'
        }
    ]
    
    for cat_data in categories:
        existing = Category.query.filter_by(name=cat_data['name']).first()
        if not existing:
            category = Category(**cat_data)
            db.session.add(category)
    
    db.session.commit()
    logger.info(f"Seeded {len(categories)} categories")


def seed_tags():
    """Seed initial tags"""
    tags = [
        'javascript', 'python', 'react', 'nodejs', 'typescript',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp',
        'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
        'git', 'ci/cd', 'testing', 'security', 'api',
        'database', 'sql', 'nosql', 'mongodb', 'postgresql',
        'html', 'css', 'vue', 'angular', 'svelte',
        'golang', 'rust', 'java', 'csharp', 'swift'
    ]
    
    for tag_name in tags:
        existing = Tag.query.filter_by(name=tag_name).first()
        if not existing:
            tag = Tag(name=tag_name)
            db.session.add(tag)
    
    db.session.commit()
    logger.info(f"Seeded {len(tags)} tags")


def seed_concepts():
    """Seed initial concepts"""
    concepts_data = [
        # Web Development Concepts
        {
            'title': 'Understanding React Hooks',
            'short_description': 'Learn how React Hooks revolutionized state management in functional components',
            'content': '''# Understanding React Hooks

## What are React Hooks?

React Hooks are functions that allow you to use state and other React features in functional components. Introduced in React 16.8, they provide a more direct API to the React concepts you already know.

## Common Hooks

### useState
The `useState` hook lets you add state to functional components:

```javascript
const [count, setCount] = useState(0);
```

### useEffect
The `useEffect` hook lets you perform side effects in functional components:

```javascript
useEffect(() => {
    document.title = `Count: ${count}`;
}, [count]);
```

### useContext
Access context values without wrapping components in Consumer:

```javascript
const theme = useContext(ThemeContext);
```

## Best Practices

1. Only call hooks at the top level
2. Only call hooks from React functions
3. Use custom hooks to share logic between components

## Benefits

- Simpler code structure
- Better code reuse
- Easier testing
- No more "this" binding issues
            ''',
            'difficulty': 'intermediate',
            'category': 'Web Development',
            'tags': ['react', 'javascript', 'hooks']
        },
        {
            'title': 'REST API Design Principles',
            'short_description': 'Master the fundamentals of designing RESTful APIs',
            'content': '''# REST API Design Principles

## What is REST?

REST (Representational State Transfer) is an architectural style for designing networked applications. It relies on a stateless, client-server communication protocol.

## Key Principles

### 1. Resource-Based
- Everything is a resource
- Resources are identified by URIs
- Resources are separate from their representations

### 2. HTTP Methods
- GET: Retrieve resources
- POST: Create new resources
- PUT: Update existing resources
- DELETE: Remove resources
- PATCH: Partial updates

### 3. Stateless
Each request contains all information needed to understand it.

### 4. Uniform Interface
Consistent naming conventions and response formats.

## Best Practices

1. Use nouns for endpoints: `/users`, not `/getUsers`
2. Use proper HTTP status codes
3. Version your API: `/api/v1/users`
4. Implement pagination for large datasets
5. Use JSON for data exchange

## Example

```
GET /api/v1/users          # Get all users
GET /api/v1/users/123      # Get specific user
POST /api/v1/users         # Create new user
PUT /api/v1/users/123      # Update user
DELETE /api/v1/users/123   # Delete user
```
            ''',
            'difficulty': 'beginner',
            'category': 'Web Development',
            'tags': ['api', 'rest', 'web-development']
        },
        
        # Machine Learning Concepts
        {
            'title': 'Introduction to Neural Networks',
            'short_description': 'Understand the basics of neural networks and deep learning',
            'content': '''# Introduction to Neural Networks

## What are Neural Networks?

Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) that process information using connectionist approaches.

## Components

### 1. Neurons
Basic units that receive input, process it, and produce output.

### 2. Layers
- **Input Layer**: Receives initial data
- **Hidden Layers**: Process information
- **Output Layer**: Produces final result

### 3. Weights and Biases
Parameters that are adjusted during training.

### 4. Activation Functions
- ReLU (Rectified Linear Unit)
- Sigmoid
- Tanh
- Softmax

## How They Learn

1. **Forward Propagation**: Input flows through the network
2. **Loss Calculation**: Compare output with expected result
3. **Backpropagation**: Adjust weights based on error
4. **Repeat**: Continue until model converges

## Applications

- Image recognition
- Natural language processing
- Game playing
- Medical diagnosis
- Financial predictions

## Simple Example (Python)

```python
import numpy as np

class SimpleNeuralNetwork:
    def __init__(self):
        self.weights = np.random.randn(2, 1)
        self.bias = 0
    
    def forward(self, X):
        return np.dot(X, self.weights) + self.bias
```
            ''',
            'difficulty': 'intermediate',
            'category': 'Machine Learning',
            'tags': ['machine-learning', 'neural-networks', 'deep-learning']
        },
        
        # Cloud Computing Concepts
        {
            'title': 'Docker Containers Explained',
            'short_description': 'Learn the fundamentals of containerization with Docker',
            'content': '''# Docker Containers Explained

## What is Docker?

Docker is a platform for developing, shipping, and running applications in containers. Containers package software and its dependencies together.

## Key Concepts

### 1. Images
Read-only templates containing application code, runtime, libraries, and dependencies.

### 2. Containers
Running instances of images. Lightweight and portable.

### 3. Dockerfile
Text file with instructions to build a Docker image.

### 4. Registry
Storage and distribution system for Docker images (e.g., Docker Hub).

## Benefits

- **Consistency**: Same environment everywhere
- **Isolation**: Applications run in separate containers
- **Portability**: Run anywhere Docker is installed
- **Efficiency**: Lighter than virtual machines

## Basic Commands

```bash
# Build an image
docker build -t myapp .

# Run a container
docker run -d -p 3000:3000 myapp

# List containers
docker ps

# Stop a container
docker stop [container-id]
```

## Sample Dockerfile

```dockerfile
FROM node:14
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```
            ''',
            'difficulty': 'beginner',
            'category': 'DevOps',
            'tags': ['docker', 'containers', 'devops']
        },
        
        # More concepts...
        {
            'title': 'Understanding HTTPS and SSL/TLS',
            'short_description': 'Learn how HTTPS secures web communications',
            'content': '''# Understanding HTTPS and SSL/TLS

## What is HTTPS?

HTTPS (Hypertext Transfer Protocol Secure) is the secure version of HTTP. It uses SSL/TLS to encrypt data between client and server.

## How It Works

### 1. SSL/TLS Handshake
1. Client hello: Browser sends supported cipher suites
2. Server hello: Server chooses cipher and sends certificate
3. Certificate verification: Client verifies server identity
4. Key exchange: Establish shared secret
5. Secure connection established

### 2. Encryption
- **Symmetric encryption**: Fast, uses same key for encrypt/decrypt
- **Asymmetric encryption**: Public/private key pairs
- **Hybrid approach**: Asymmetric for key exchange, symmetric for data

### 3. Certificate Authority (CA)
Trusted third party that issues digital certificates.

## Benefits

- **Confidentiality**: Data is encrypted
- **Integrity**: Data can't be modified
- **Authentication**: Verify server identity

## Implementation

```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```
            ''',
            'difficulty': 'intermediate',
            'category': 'Cybersecurity',
            'tags': ['security', 'https', 'ssl', 'tls']
        }
    ]
    
    # Get categories and tags
    categories = {cat.name: cat for cat in Category.query.all()}
    tags = {tag.name: tag for tag in Tag.query.all()}
    
    for concept_data in concepts_data:
        # Check if concept already exists
        existing = Concept.query.filter_by(title=concept_data['title']).first()
        if existing:
            continue
            
        # Extract category and tags
        category_name = concept_data.pop('category')
        tag_names = concept_data.pop('tags', [])
        
        # Create concept
        concept = Concept(**concept_data)
        concept.category = categories.get(category_name)
        
        # Add tags
        for tag_name in tag_names:
            if tag_name in tags:
                concept.tags.append(tags[tag_name])
        
        db.session.add(concept)
    
    db.session.commit()
    logger.info(f"Seeded {len(concepts_data)} concepts")


def seed_database():
    """Main seeding function"""
    app = create_app()
    with app.app_context():
        logger.info("Starting database seeding...")
        
        # Create tables if they don't exist
        db.create_all()
        
        # Seed data
        seed_categories()
        seed_tags()
        seed_concepts()
        
        logger.info("Database seeding completed!")


if __name__ == "__main__":
    seed_database()