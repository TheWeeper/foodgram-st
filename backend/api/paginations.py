from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class FoodgramPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_query_param = 'page'
