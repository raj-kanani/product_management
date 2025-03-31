from django.urls import path
from .views import *
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("products/", ProductListAPIView.as_view(), name="product_list"),
    path("import_product/", import_products, name="import_product"),
    path('token/', obtain_auth_token, name='api_token_auth'),

]
