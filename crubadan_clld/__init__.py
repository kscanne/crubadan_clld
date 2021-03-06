from clld.web.app import menu_item, get_configurator
from clld.web.datatables.base import DataTable
from functools import partial

from crubadan_clld import models
from crubadan_clld import interfaces


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = get_configurator('crubadan_clld', settings=settings)
    config.include('crubadan_clld.datatables')
    config.include('crubadan_clld.adapters')

    # Set up redundant route to dist files for backwards-compatibility
    config.add_static_view('dist', '/data/crubadan-clld/files')

    # Set up route for OLAC xml file
    # This route overrides clld's builtin 'olac' route
    config.commit() # (bypasses the override error)
    config.add_route_and_view('olac', '/olac.xml', views.olac_xml)
    
    config.register_resource(
        'writingsystem',
        models.WritingSystem,
        interfaces.IWritingSystem,
        with_index=True,
    )

    config.register_menu(
        ('dataset', partial(menu_item, 'dataset', label='Home')),
        ('writingsystems', partial(menu_item, 'writingsystems',
                                    label='Downloads')),
        ('apps', partial(menu_item, 'apps', label='Applications')),
        ('acks', partial(menu_item, 'acks', label='Acknowledgements'))
    )

    config.add_route_and_view(
        'apps',
        '/applications',
        views.apps,
        renderer='apps.mako'
    )

    config.add_route_and_view(
        'acks',
        '/acknowldegments',
        views.acks,
        renderer='acks.mako'
    )

    return config.make_wsgi_app()
