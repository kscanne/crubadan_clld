from clld.web.maps import Map, Legend
from clld.web.util.htmllib import HTML, literal
from clld.web.util.helpers import marker_img

def includeme(config):
    config.register_map('writingsystems', Map)
