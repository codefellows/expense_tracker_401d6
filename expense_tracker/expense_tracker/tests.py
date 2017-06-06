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


def test_create_view_post_empty_data_returns_empty_dict(post_request):
    from expense_tracker.views.default import create_view
    response = create_view(post_request)
    assert response == {}


def test_create_view_post_incomplete_data_returns_error(post_request):
    from expense_tracker.views.default import create_view
    data = {
        'title': '',
        'price': ''
    }
    post_request.POST = data
    response = create_view(post_request)
    assert 'error' in response


def test_create_view_post_incomplete_data_returns_data(post_request):
    from expense_tracker.views.default import create_view
    data = {
        'title': 'flerg the blerg',
        'price': ''
    }
    post_request.POST = data
    response = create_view(post_request)
    assert 'title' in response
    assert 'price' in response
    assert response['title'] == 'flerg the blerg'
    assert response['price'] == ''


def test_create_view_post_with_data_redirects(post_request):
    from expense_tracker.views.default import create_view
    from pyramid.httpexceptions import HTTPFound
    data = {
        'title': 'flerg the blerg',
        'price': '5000',
        'description': ''
    }
    post_request.POST = data
    response = create_view(post_request)
    assert response.status_code == 302
    assert isinstance(response, HTTPFound)


@pytest.fixture(scope="session")
def testapp(request):
    from webtest import TestApp
    from pyramid.config import Configurator

    def main(global_config, **settings):
        """ This function returns a Pyramid WSGI application.
        """
        settings['sqlalchemy.url'] = "postgres:///test_expenses"
        config = Configurator(settings=settings)
        config.include('pyramid_jinja2')
        config.include('.models')
        config.include('.routes')
        config.scan()
        return config.make_wsgi_app()

    app = main({})
    testapp = TestApp(app)

    SessionFactory = app.registry["dbsession_factory"]
    engine = SessionFactory().bind
    Base.metadata.create_all(bind=engine)

    def tearDown():
        Base.metadata.drop_all(bind=engine)

    request.addfinalizer(tearDown)

    return testapp


def test_new_expense_redirects_to_home(testapp):
    """When redirection is followed, result is home page."""
    data = {
        'title': 'flerg the blerg',
        'price': '5000',
        'description': ''
    }
    response = testapp.post('/expense/new-expense', data)
    assert response.location == SITE_ROOT + "/"


def test_new_expense_redirects_to_home_and_shows_html(testapp):
    """When redirection is followed, result is home page."""
    data = {
        'title': 'flerg the blerg',
        'price': '5000',
        'description': ''
    }
    response = testapp.post('/expense/new-expense', data).follow()
    assert "<h1>List of Expenses</h1>" in response.text
