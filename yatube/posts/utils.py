from django.core.paginator import Paginator
from django.conf import settings


def pagination_fun(some_list, request):
    page_number = request.GET.get('page')
    page_obj = Paginator(some_list, settings.POSTS_LIMIT).get_page(page_number)
    return page_obj
