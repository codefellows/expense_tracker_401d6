from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound
from expense_tracker.views.default import EXPENSES
import pytest


@pytest.fixture
def home_response():
    """Return a response from the home page."""
    from expense_tracker.views.default import home_view
    request = testing.DummyRequest()
    response = home_view(request)
    return response


def test_home_view_returns_proper_content(home_response):
    """Home view response includes the content we added."""
    assert "page" in home_response
    assert "expenses" in home_response
    assert home_response["expenses"] == EXPENSES


def test_detail_view_with_id_returns_one_expense():
    """."""
    from expense_tracker.views.default import detail_view
    req = testing.DummyRequest()
    req.matchdict['id'] = '1'
    response = detail_view(req)
    assert response['expense'] == EXPENSES[1]


def test_detail_view_with_bad_id_raises_exception():
    """."""
    from expense_tracker.views.default import detail_view
    req = testing.DummyRequest()
    req.matchdict['id'] = '100'
    with pytest.raises(HTTPNotFound):
        detail_view(req)


# ======== FUNCTIONAL TESTS START HERE =========


@pytest.fixture
def testapp():
    """Create a test application to use for functional tests."""
    from expense_tracker import main
    from webtest import TestApp
    app = main({})
    return TestApp(app)


def test_home_route_returns_home_content(testapp):
    """."""
    response = testapp.get('/')
    html = response.html
    assert 'List of Expenses' in str(html.find('h1').text)
    assert 'Expense Tracker | Home' in str(html.find('title').text)


def test_home_route_listing_has_all_expenses(testapp):
    """."""
    response = testapp.get('/')
    html = response.html
    assert len(EXPENSES) == len(html.find_all('li'))


def test_detail_route_with_bad_id(testapp):
    """."""
    response = testapp.get('/expense/400', status=404)
    assert "OOOOOOOOH MY GOOOOOOOOOOD!!!!" in response.text
