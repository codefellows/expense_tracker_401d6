import pytest
from pyramid import testing
import transaction
from expense_tracker.models import (
    Expense,
    get_tm_session,
)
from expense_tracker.models.meta import Base

SITE_ROOT = 'http://localhost'


@pytest.fixture(scope="session")
def configuration(request):
    """Set up a Configurator instance.

    This Configurator instance sets up a pointer to the location of the
        database.
    It also includes the models from your app's model package.
    Finally it tears everything down, including the in-memory SQLite database.

    This configuration will persist for the entire duration of your PyTest run.
    """
    config = testing.setUp(settings={
        'sqlalchemy.url': 'postgres://localhost:5432/test_expenses'
    })
    config.include("expense_tracker.models")
    config.include("expense_tracker.routes")

    def teardown():
        testing.tearDown()

    request.addfinalizer(teardown)
    return config


@pytest.fixture
def db_session(configuration, request):
    """Create a session for interacting with the test database.

    This uses the dbsession_factory on the configurator instance to create a
    new database session. It binds that session to the available engine
    and returns a new session for every call of the dummy_request object.
    """
    SessionFactory = configuration.registry["dbsession_factory"]
    session = SessionFactory()
    engine = session.bind
    Base.metadata.create_all(engine)

    def teardown():
        session.transaction.rollback()
        Base.metadata.drop_all(engine)

    request.addfinalizer(teardown)
    return session


@pytest.fixture
def dummy_request(db_session):
    from pyramid import testing
    req = testing.DummyRequest()
    req.dbsession = db_session
    return req


@pytest.fixture
def post_request(dummy_request):
    dummy_request.method = "POST"
    return dummy_request


@pytest.fixture
def set_credentials():
    from expense_tracker.security import context
    import os
    os.environ['AUTH_PASSWORD'] = context.hash('flamingo')


# def test_create_view_post_empty_data_returns_empty_dict(post_request):
#     from expense_tracker.views.default import create_view
#     response = create_view(post_request)
#     assert response == {}


# def test_create_view_post_incomplete_data_returns_error(post_request):
#     from expense_tracker.views.default import create_view
#     data = {
#         'title': '',
#         'price': ''
#     }
#     post_request.POST = data
#     response = create_view(post_request)
#     assert 'error' in response


# def test_create_view_post_incomplete_data_returns_data(post_request):
#     from expense_tracker.views.default import create_view
#     data = {
#         'title': 'flerg the blerg',
#         'price': ''
#     }
#     post_request.POST = data
#     response = create_view(post_request)
#     assert 'title' in response
#     assert 'price' in response
#     assert response['title'] == 'flerg the blerg'
#     assert response['price'] == ''


# def test_create_view_post_with_data_redirects(post_request):
#     from expense_tracker.views.default import create_view
#     from pyramid.httpexceptions import HTTPFound
#     data = {
#         'title': 'flerg the blerg',
#         'price': '5000',
#         'description': ''
#     }
#     post_request.POST = data
#     response = create_view(post_request)
#     assert response.status_code == 302
#     assert isinstance(response, HTTPFound)


# def test_login_bad_credentials_fails(post_request):
#     from expense_tracker.views.default import login
#     data = {
#         'username': 'sea_python_401d6',
#         'password': 'not_potato'
#     }
#     post_request.POST = data
#     response = login(post_request)
#     assert response == {'error': 'Bad username or password'}


# def test_login_empty_credentials_fails(post_request):
#     from expense_tracker.views.default import login
#     data = {
#         'username': '',
#         'password': ''
#     }
#     post_request.POST = data
#     response = login(post_request)
#     assert response == {'error': 'Bad username or password'}


# def test_get_login_returns_dict(dummy_request):
#     from expense_tracker.views.default import login
#     dummy_request.method = "GET"
#     response = login(dummy_request)
#     assert response == {}


# def test_login_successful_with_good_creds(post_request, set_credentials):
#     from expense_tracker.views.default import login
#     from pyramid.httpexceptions import HTTPFound
#     data = {
#         'username': 'sea_python_401d6',
#         'password': 'flamingo'
#     }
#     post_request.POST = data
#     response = login(post_request)
#     assert isinstance(response, HTTPFound)


# def test_logout_redirects(dummy_request):
#     from expense_tracker.views.default import logout
#     from pyramid.httpexceptions import HTTPFound
#     response = logout(dummy_request)
#     assert isinstance(response, HTTPFound)


def test_api_list_returns_dictionary_with_expense_list(dummy_request):
    from expense_tracker.views.default import api_list
    response = api_list(dummy_request)
    query = dummy_request.dbsession.query(Expense).all()
    assert len(response) == len(query)
    for item in query:
        assert item.to_json() in response


# ========== INTEGRATION TESTS AFTER THIS POINT =========

# @pytest.fixture(scope="session")
# def testapp(request):
#     from webtest import TestApp
#     from pyramid.config import Configurator

#     def main(global_config, **settings):
#         """ This function returns a Pyramid WSGI application.
#         """
#         settings['sqlalchemy.url'] = "postgres:///test_expenses"
#         config = Configurator(settings=settings)
#         config.include('pyramid_jinja2')
#         config.include('expense_tracker.models')
#         config.include('expense_tracker.routes')
#         config.include('expense_tracker.security')
#         config.scan()
#         return config.make_wsgi_app()

#     app = main({})
#     testapp = TestApp(app)

#     SessionFactory = app.registry["dbsession_factory"]
#     engine = SessionFactory().bind
#     Base.metadata.create_all(bind=engine)

#     def tearDown():
#         Base.metadata.drop_all(bind=engine)

#     request.addfinalizer(tearDown)

#     return testapp


# def test_unauthenticated_user_is_forbidden_from_create_route(testapp):
#     response = testapp.get('/expense/new-expense', status=403)
#     assert response.status_code == 403


# def test_unauthenticated_user_is_forbidden_from_update_route(testapp):
#     response = testapp.get('/expense/1/edit', status=403)
#     assert response.status_code == 403


# def test_can_get_login_route(testapp):
#     response = testapp.get('/login')
#     assert response.status_code == 200


# def test_get_login_route_has_form_and_fields(testapp):
#     response = testapp.get('/login')
#     html = response.html
#     assert html.find('form').attrs['method'] == 'POST'
#     assert html.find('input', type='submit').attrs['value'] == 'Log In'
#     assert html.find('input', {'name': 'username'})
#     assert html.find('input', {'name': 'password'})


# def test_post_login_route_with_bad_creds(testapp):
#     response = testapp.post('/login', {
#         'username': 'sea_python_401d6',
#         'password': 'fhwqwgads'
#     })
#     assert response.status_code == 200
#     html = response.html
#     assert html.find('form').attrs['method'] == 'POST'
#     assert html.find('input', type='submit').attrs['value'] == 'Log In'
#     assert html.find('input', {'name': 'username'})
#     assert html.find('input', {'name': 'password'})
#     # assert response.location == SITE_ROOT + '/login'


# def test_post_login_route_with_good_creds(testapp):
#     response = testapp.post('/login', {
#         'username': 'sea_python_401d6',
#         'password': 'flamingo'
#     })
#     assert 'auth_tkt' in response.headers['Set-Cookie']
#     assert response.status_code == 302
#     assert response.location == SITE_ROOT + '/'


# def test_new_expense_no_token_fails(testapp):
#     """When redirection is followed, result is home page."""
#     data = {
#         'title': 'flerg the blerg',
#         'price': '5000',
#         'description': ''
#     }
#     response = testapp.post('/expense/new-expense', data, status=400)
#     assert response.status_code == 400


# def test_new_expense_redirects_to_home(testapp):
#     """When redirection is followed, result is home page."""
#     response1 = testapp.get('/expense/new-expense')
#     token = response1.html.find('input', type='hidden').attrs['value']
#     data = {
#         'title': 'flerg the blerg',
#         'price': '5000',
#         'description': '',
#         'csrf_token': token
#     }
#     response = testapp.post('/expense/new-expense', data)
#     assert response.location == SITE_ROOT + "/"


# def test_edit_non_existent_expense_raises_404(testapp):
#     response = testapp.get('/expense/100/edit', status=404)
#     assert "<h1>OOOOOOOOH MY GOOOOOOOOOOD!!!!</h1>" in response.text


# def test_new_expense_redirects_to_home_and_shows_html(testapp):
#     """When redirection is followed, result is home page."""
#     response1 = testapp.get('/expense/new-expense')
#     token = response1.html.find('input', type='hidden').attrs['value']

#     data = {
#         'title': 'flerg the blerg',
#         'price': '5000',
#         'description': '',
#         'csrf_token': token
#     }
#     response = testapp.post('/expense/new-expense', data).follow()
#     assert "<h1>List of Expenses</h1>" in response.text
