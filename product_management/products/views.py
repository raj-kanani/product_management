import csv
import threading
import queue

from django.contrib.auth import authenticate
from django.contrib.messages.storage import default_storage
from django.http import JsonResponse
from django.core.files.storage import default_storage

from rest_framework.generics import ListCreateAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication

from .models import Product
from .serializers import ProductSerializer


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


def process_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        # Add data from csv
        for row in reader:
            product_queue.put(row)

    while not product_queue.empty():
        data = product_queue.get()
        Product.objects.update_or_create(
            handle=data["Handle"],
            defaults={
                "title": data["Title"],
                "body": data["Body"],
                "vendor": data["Vendor"],
                "type": data["Type"],
                "tags": data["Tags"],
                "published": data["Published"] == 'TRUE',
                "variant_sku": data["Variant SKU"],
                "variant_inventory_tracker": data["Variant Inventory Tracker"],
                "variant_price": data["Variant Price"],
                "image_src": data["Image Src"],
            }

        )

        product_queue.task_done()

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def import_products(request):
    if "file" not in request.FILES:
        return Response({"error": "CSV file required"}, status=400)

    file = request.FILES['file']
    # Get file using arg
    file_path = default_storage.save("products_export_1.csv", file)
    print(file_path, 'file path')

    # Generate thread process
    thread = threading.Thread(target=process_csv, args=(file_path, None))
    thread.start()

    return JsonResponse({"message": "Product import "})


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

