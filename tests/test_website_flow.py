from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from aspen.http.request import Request
from aspen.http.response import Response


def test_website_can_respond(harness):
    harness.fs.www.mk(('index.html.spt', 'Greetings, program!'))
    assert harness.client.GET().body == 'Greetings, program!'


def test_404_comes_out_404(harness):
    harness.fs.project.mk(('404.spt', '[---]\n[---] text/plain\nEep!'))
    assert harness.client.GET(raise_immediately=False).code == 404


def test_request_context_can_be_populated_by_user(harness):
    harness.fs.www.mk(('index.html.spt', '%(foo)s'))
    harness.fs.project.mk(('configure-aspen.py', """\
def add_foo_to_context(request):
    request.context['foo'] = 'bar'

website.algorithm.insert_after('parse_environ_into_request', add_foo_to_context)
"""))
    assert harness.client.GET().body == 'bar'


def test_early_failures_dont_break_everything(harness):
    old_from_wsgi = Request.from_wsgi
    def broken_from_wsgi(*a, **kw):
        raise Response(400)
    try:
        Request.from_wsgi = classmethod(broken_from_wsgi)
        assert harness.client.GET("/", raise_immediately=False).code == 400
    finally:
        Request.from_wsgi = old_from_wsgi
