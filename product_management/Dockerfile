# Base image: Python 3.13 slim version for a minimal footprint
FROM python:3.10


# Set working directory for all subsequent commands
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app/
EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]