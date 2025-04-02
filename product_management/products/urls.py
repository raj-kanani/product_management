from django.urls import path
from .views import *
from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("products/", ProductListAPIView.as_view(), name="product_list"),
    path("import_product/", import_products, name="import_product"),
    path("search-products/", search_products, name="search_products"),
    path("delete-product/", delete_product, name="delete_product"),
    path('generate-products/', generate_product_view, name='generate_products'),
    path('token/', obtain_auth_token, name='api_token_auth'),


]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
