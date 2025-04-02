import csv
import threading
import queue

from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.messages.storage import default_storage
from django.http import JsonResponse
from django.core.files.storage import default_storage
from celery import shared_task
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from rest_framework.generics import ListCreateAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication

from .models import Product
from .serializers import ProductSerializer

@csrf_exempt
@api_view(["POST"])
def generate_token(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username, password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    else:
        return Response({'error': 'Invalid credentials'}, status=401)

class ProductPagination(PageNumberPagination):
    page_size = 10


product_queue = queue.Queue()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def import_products(request):
    if "file" not in request.FILES:
        return Response({"error": "CSV file required"}, status=400)

    file = request.FILES['file']
    # Get file using arg
    file_path = default_storage.save("products/" + file.name, file)
    print(file_path, 'file path')

    absolute_path = default_storage.path(file_path)
    print(absolute_path, "absolute path")
    # Generate thread process
    thread = threading.Thread(target=process_csv, args=(absolute_path,))
    thread.start()

    return JsonResponse({"message": "Product import successfully "})


def process_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        # Add data from csv
        for row in reader:
            # product_queue.put(row)
            handle = row["Handle"]
            title = row["Title"]
            body = row["Body (HTML)"]
            vendor = row["Vendor"]
            type = row["Type"]
            tags = row["Tags"]
            published = row["Published"]
            variant_sku = row["Variant SKU"]
            # variant_inventory_tracker = row["Variant Inventory Tracker"]
            variant_price = row["Variant Price"]
            image_src = row["Image Src"]

        product, created = Product.objects.update_or_create(
            handle= handle,
            defaults={
                "title": title,
                "body": body,
                "vendor": vendor,
                "type": type,
                "tags": tags,
                "published": published,
                "variant_sku": variant_sku,
                # "variant_inventory_tracker": variant_inventory_tracker,
                "variant_price": variant_price,
                "image_src": image_src,
            }

        )
        print(f"product processed:{title}, created:{created}")

    print(f"Error processing file")

class ProductListAPIView(ListCreateAPIView):
    queryset = Product.objects.filter(is_deleted=False)
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    def get_queryset(self):
        search_data = self.request.query_params.get('search', "")
        # search product on product title field.
        return Product.objects.filter(title__icontains=search_data, is_deleted=False)

import random
@shared_task
def generate_products(num_products):
    products = [
        Product(
            handle = f"product-{random.randint(1000, 9000)}",
            title = f"product-{random.randint(1, 1000)}",
            image_src = "http://google.com/100", type=random.choice(["Electronics", "Clothing", "Furniture"]),
            variant_price = round(random.uniform(10,500)),
            variant_sku = f"SKU{random.randint(1000, 9999)}",
            published = random.choice([True, False]) )
            for _ in range (num_products)
        ]

    Product.objects.bulk_create(products)
    return f"{num_products} product generated successfully"

def generate_product_view(request):
    if request.method == "POST":
        num_products = int(request.POST.get("num_products", 0))
        generate_products.delay(num_products)
        return JsonResponse({"message": "Product generate using celery" })
    return render(request, 'generate_products.html')