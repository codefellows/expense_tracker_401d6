"""Views for the Expense Tracker application."""
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound

EXPENSES = [
    {'id': 0, 'title': 'Pizza', 'price': 5000},
    {'id': 1, 'title': 'Cheese', 'price': 500},
    {'id': 2, 'title': 'Eggs', 'price': 20},
    {'id': 3, 'title': 'Juice', 'price': 50},
    {'id': 4, 'title': 'Crackers', 'price': 1000},
    {'id': 5, 'title': 'Grapes', 'price': 750},
    {'id': 6, 'title': 'Rent', 'price': 50000}
]


@view_config(route_name='home', renderer='../templates/list.jinja2')
def home_view(request):
    """View for the home route."""
    return {
        'page': 'Home',
        'expenses': EXPENSES
    }


@view_config(route_name='detail', renderer="../templates/detail.jinja2")
def detail_view(request):
    """View for the detail route."""
    the_id = int(request.matchdict['id'])
    try:
        expense = EXPENSES[the_id]
    except IndexError:
        raise HTTPNotFound

    return {
        'page': 'Expense Info',
        'expense': expense
    }
