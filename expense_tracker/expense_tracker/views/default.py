"""Views for the Expense Tracker application."""
import io, os
from pyramid.response import Response

HERE = os.path.dirname(__file__)


def home_page(request):
    """View for the home route."""
    with io.open(os.path.join(HERE, 'sample.html')) as the_file:
        imported_text = the_file.read()

    return Response(imported_text)
