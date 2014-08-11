# -*- coding: utf-8 -*-
from pyramid.events import subscriber
from pyramid.renderers import get_renderer
from pyramid.security import forget, remember

from h import events


@subscriber(events.BeforeRender)
def add_renderer_globals(event):
    request = event['request']

    # Set the base url to use in the <base> tag
    if hasattr(request, 'root'):
        event['base_url'] = request.resource_url(request.root, '')

    # Set the service url to use for API discovery
    event['service_url'] = request.route_url('api', subpath='')

    # Set the blocks property to refer to the block helpers template
    event['blocks'] = get_renderer('h:templates/blocks.pt').implementation()


@subscriber(events.NewResponse, asset_request=False)
def set_csrf_cookie(event):
    request = event.request
    response = event.response
    session = request.session

    if session.keys():
        token = session.get_csrf_token()
        if request.cookies.get('XSRF-TOKEN') != token:
            response.set_cookie('XSRF-TOKEN', token)
    elif 'XSRF-TOKEN' in request.cookies:
        response.delete_cookie('XSRF-TOKEN')


@subscriber(events.LoginEvent)
def login(event):
    request = event.request
    user = event.user
    request.response.headerlist.extend(remember(request, user))

    # bw compat
    session = request.session
    personas = session.setdefault('personas', [])

    if user not in personas:
        personas.append(user)
        session.changed()


@subscriber(events.LogoutEvent)
def logout(event):
    request = event.request
    forget(request)
    request.session.invalidate()


def includeme(config):
    config.scan(__name__)
