from rest_framework.pagination import PageNumberPagination


class ModifiedPageNumberPagination(PageNumberPagination):
    """PageNumberPagination with custom `page size` query param name."""
    page_size_query_param = 'limit'
    page_size = 20
    max_page_size = 1000
