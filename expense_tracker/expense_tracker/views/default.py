"""Views for the Expense Tracker application."""
from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPFound
)
from pyramid.security import remember, forget
from expense_tracker.models import Expense
from expense_tracker.security import check_credentials
import datetime


@view_config(route_name='home', renderer='../templates/list.jinja2')
def home_view(request):
    """View for the home route."""
    session = request.dbsession
    all_expenses = session.query(Expense).order_by(Expense.paid_date.desc()).all()
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


@view_config(
    route_name="create",
    renderer="../templates/new-expense.jinja2",
    permission="secret"
)
def create_view(request):
    """View for adding a new expense to the database."""
    if request.method == "POST" and request.POST:
        if not request.POST['title'] or not request.POST['price']:
            return {
                'title': request.POST['title'],
                'price': request.POST['price'],
                'error': "Hey dude, you're missing a little something"
            }
        new_expense = Expense(
            title=request.POST['title'],
            price=int(request.POST['price']),
            description=request.POST['description'],
            paid_date=datetime.datetime.now()
        )
        request.dbsession.add(new_expense)
        return HTTPFound(
            location=request.route_url('home')
        )

    return {}


@view_config(
    route_name="update",
    renderer="../templates/edit-expense.jinja2",
    permission="secret"
)
def update_view(request):
    # if given a bad id, raise a not found exception
    the_id = int(request.matchdict['id'])
    session = request.dbsession
    expense = session.query(Expense).get(the_id)
    if not expense:
        raise HTTPNotFound
    # with a get request, show the existing content in the form
    if request.method == "GET":
        return {
            "page": "Edit Page",
            "title": expense.title,
            "price": expense.price,
            "description": expense.description
        }
    # with a post request, add the updated content to the database
    if request.method == "POST":
        expense.title = request.POST['title']
        expense.price = int(request.POST['price'])
        expense.description = request.POST['description']
        request.dbsession.flush()
        return HTTPFound(request.route_url('detail', id=expense.id))


@view_config(route_name='login', renderer='../templates/login.jinja2', require_csrf=False)
def login(request):
    """View for logging in a user."""
    if request.method == "GET":
        return {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        if check_credentials(username, password):
            headers = remember(request, username)
            return HTTPFound(
                location=request.route_url('home'),
                headers=headers
            )
        return {'error': 'Bad username or password'}


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)


@view_config(route_name='test', renderer='json')
def test_view(request):
    return {"foo": "bar"}
