from django.urls import path
from .views import *
from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("products/", ProductListAPIView.as_view(), name="product_list"),
    path("import_product/", import_products, name="import_product"),
    path('token/', obtain_auth_token, name='api_token_auth'),
    path('generate-products/', generate_product_view, name='generate_product'),
    path('token/', obtain_auth_token, name='api_token_auth'),


]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
