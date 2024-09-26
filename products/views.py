from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User

from .models import Product
from .permissions import ProductPermission
from .serializers import ProductSerializer
from .services import get_presigned_product


class UserProductPagination(PageNumberPagination):
    """
    Pagination for UserViewSet
    """

    page_size = 10
    page_size_query_param = None
    max_page_size = 10


class GetPresignedUrlView(APIView):
    """
    POST /Products/presigned/: get AWS S3 Bucket presigned Product url
    """

    permission_classes = (IsAuthenticated,)
    throttle_scope = "GetPresignedUrlView"

    def product(self, request):
        try:
            presigned_url = get_presigned_product()
            return Response(presigned_url)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductListView(generics.ListAPIView):
    """
    Base class for listing products with optional user filter and pagination.
    """

    permission_classes = (AllowAny,)
    serializer_class = ProductSerializer
    pagination_class = UserProductPagination

    def get_queryset(self):
        return Product.objects.all()


class LatestProductsViaHandleAPIView(generics.ListAPIView):
    """
    GET /products/latest/{handle}: return latest product via user
    /products/latest/{handle}/?page=2: return latest product via user and pagination
    """

    def get_queryset(self):
        handle = self.kwargs.get("handle")
        user = get_object_or_404(User, handle=handle)
        return Product.filter(user=user).order_by("-created_at")


class LatestProductsAPIView(generics.ListAPIView):
    """
    GET /products/latest/{handle}: return latest product via user
    /products/latest/{handle}/?page=2: return latest product via user and pagination
    """


class RecommendPostsAPIView(generics.ListAPIView):
    """
    GET /products/recommend: return recommended products
    """


class ProductViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    POST /product/p/: Create a new product via data
    GET /product/p/{uuid}: Get product[uuid] detail
    PUT /product/p/{uuid}: Update product[uuid]
    DELETE /product/p/{uuid}: Delete product[uuid]
    """

    permission_classes = (ProductPermission,)
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    lookup_field = "uuid"

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        pass

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
