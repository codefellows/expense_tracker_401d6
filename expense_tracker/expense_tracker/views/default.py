"""Views for the Expense Tracker application."""
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from expense_tracker.models import Expense


@view_config(route_name='home', renderer='../templates/list.jinja2')
def home_view(request):
    """View for the home route."""
    session = request.dbsession
    all_expenses = session.query(Expense).all()
    return {
        'page': 'Home',
        'expenses': all_expenses
    }


@view_config(route_name='detail', renderer="../templates/detail.jinja2")
def detail_view(request):
    """View for the detail route."""
    the_id = int(request.matchdict['id'])
    session = request.dbsession
    expense = session.query(Expense).get(the_id)
    if not expense:
        raise HTTPNotFound

    return {
        'page': 'Expense Info',
        'expense': expense
    }
