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
from .tasks import generate_products

from rest_framework.generics import ListCreateAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication

from .serializers import ProductSerializer
from django.db.models import Q
from .models import Product


def search_products(request):
    query = request.GET.get("query", "").strip().lower()

    if not query:
        products = Product.objects.all()
    else:
        products = Product.objects.filter(
            Q(handle__icontains=query) |
            Q(title__icontains=query) |
            Q(type__icontains=query) |
            Q(variant_price__icontains=query) |
            Q(variant_sku__icontains=query) |
            Q(published__icontains=query)
        )

    product_list = list(
        products.values("handle", "title", "type", "image_src", "variant_price", "variant_sku", "published"))

    return JsonResponse({"products": product_list})


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
        return JsonResponse({"error": "CSV file required"}, status=400)

    file = request.FILES['file']

    # Save the uploaded file
    file_path = default_storage.save('products/' + file.name, file)  # Path to store the file
    print(f"File saved at: {file_path}")

    # Get the absolute file path
    absolute_file_path = default_storage.path(file_path)
    print(f"Absolute file path: {absolute_file_path}")

    # Start threading to process the CSV file in the background
    thread = threading.Thread(target=process_csv, args=(absolute_file_path,))
    thread.start()

    return JsonResponse({"message": "Product import started."})


def process_csv(file_path):
    try:
        # Open the file using the absolute path
        with open(file_path, newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                # Process each row of the CSV and create Product records
                handle = row['Handle']
                title = row['Title']
                body = row['Body (HTML)']
                vendor = row['Vendor']
                type = row['Type']
                tags = row['Tags']
                published = row['Published']
                variant_sku = row['Variant SKU']
                variant_price = row['Variant Price']
                image_src = row['Image Src']

                # Create product or update existing one
                product, created = Product.objects.update_or_create(
                    handle=handle,
                    defaults={
                        'title': title,
                        'body': body,
                        'vendor': vendor,
                        'type': type,
                        'tags': tags,
                        'published': published,
                        'variant_sku': variant_sku,
                        'variant_price': variant_price,
                        'image_src': image_src,
                    }
                )

                # Print status of product creation/update
                print(f"Processed product: {title}, Created: {created}")

    except Exception as e:
        print(f"Error processing file: {e}")

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


@csrf_exempt
def generate_product_view(request):
    if request.method == "POST":
        num_products = request.POST.get("num_products")
        if not num_products or not num_products.isdigit() or int(num_products) <= 0:
            return JsonResponse({"error": "Invalid input"}, status=400)
        generate_products.delay(int(num_products))
        return JsonResponse({"message": "Product generation started using Celery."})
    return render(request, "generate_products.html")