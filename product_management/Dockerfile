# Base image: Python 3.13 slim version for a minimal footprint
FROM python:3.10.12

# Set working directory for all subsequent commands
WORKDIR /product_management
COPY ./product_management
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "product_management.wsgi:application"]
