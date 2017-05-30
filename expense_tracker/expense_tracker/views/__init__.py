from .default import home_page


def includeme(config):
    """List of views to include for the configurator object."""
    config.add_view(home_page, route_name="home")
