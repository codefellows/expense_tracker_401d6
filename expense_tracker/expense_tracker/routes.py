def includeme(config):
    config.add_static_view('static', 'expense_tracker:static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('detail', '/expense/{id:\d+}')
    config.add_route('create', '/expense/new-expense')
    config.add_route('update', '/expense/{id:\d+}/edit')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
