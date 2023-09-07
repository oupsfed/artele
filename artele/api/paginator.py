from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagePagination(PageNumberPagination):
    """
    Пагинация с добавлением поля page

    page: int - Номер страницы
    """

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('page', int(self.get_page_number(
                self.request,
                self.page.paginator
            ))),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
