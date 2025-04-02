# product_management
# Django REST API - Product Import & Management  

# Clone the repository

git clone https://github.com/raj-kanani/product_management.git  
$ cd product_management  

# Create a virtual environment  
 python3 -m venv venv  
source venv/bin/activate  # On Windows: venv\Scripts\activate  

# Install dependencies  
$ pip install -r requirements.txt  

# Apply database migrations  
$ python3 manage.py migrate  

# Create a superuser  
$ python3 manage.py createsuperuser  

# Run the development server  
$ python3 manage.py runserver  

# Start Celery for background tasks  
celery -A product_management worker --loglevel=info  

# Start Redis (Required for Celery)  
redis-server  


# Testing API endpoints : 

# Authentication

- POST : http://127.0.0.1:8000/api/token/	


# Product Import

- POST : http://127.0.0.1:8000/api/import-products/	


- curl -X POST "http://127.0.0.1:8000/api/import-products/" \
     -H "Authorization: Token your_token" \
     -F "file=@/path/to/products.csv"

# Generate random products
POST : http://127.0.0.1:8000/api/generate-products/
Payload : 
{
    "num_products":1000
}
# Soft delete & Hard delete product (via celery)
POST :http://127.0.0.1:8000/api/delete-product/
Payload : {
    "product_ids": [10,11]
}

# Search product :
GET: http://127.0.0.1:8000/api/search-products/?query=dsf

# Build docker image using container and run celery using docker

docker-compose up --build  

# Run docker with redis (optional)
docker run -d --name redis -p 6379:6379 redis

