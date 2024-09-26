from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.models import User

from .models import Product
from .permissions import ProductPermission
from .serializers import ProductCreateUpdateSerializer, ProductRetrieveSerializer


class UserProductPagination(PageNumberPagination):
    """
    Pagination for Product views
    """

    page_size = 10
    page_size_query_param = None
    max_page_size = 10


class LatestProductsViaHandleAPIView(generics.ListAPIView):
    """
    GET /products/latest/{handle}: return latest product via user
    /products/latest/{handle}/?page=2: return latest product via user and pagination
    """

    serializer_class = ProductRetrieveSerializer
    pagination_class = UserProductPagination
    permission_classes = (AllowAny,)

    def get_queryset(self):
        handle = self.kwargs.get("handle")
        user = get_object_or_404(User, handle=handle)
        return Product.objects.filter(user=user).order_by("-created_at")


class RecommendProductsAPIView(generics.ListAPIView):
    """
    GET /products/recommend: return recommended products
    """

    serializer_class = ProductRetrieveSerializer
    pagination_class = UserProductPagination
    permission_classes = (AllowAny,)

    def get_queryset(self):
        # Random 10 products for example
        # Implement recommendation logic later
        return Product.objects.all().order_by("?")[:10]


class ProductViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    POST /product/p/: Create a new product via data
    GET /product/p/: List all products
    GET /product/p/{uuid}: Get product[uuid] detail
    PUT /product/p/{uuid}: Update product[uuid]
    DELETE /product/p/{uuid}: Delete product[uuid]
    """

    permission_classes = (ProductPermission,)
    queryset = Product.objects.all()
    lookup_field = "uuid"
    pagination_class = UserProductPagination

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProductCreateUpdateSerializer
        return ProductRetrieveSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
