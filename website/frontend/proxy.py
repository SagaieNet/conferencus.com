from werkzeug.exceptions import HTTPException, PreconditionRequired, PreconditionFailed
import flask
import datetime

from ..utils import get_modified, get_file

def image_response(path):
    etag, last_modified = get_modified(path)

    if flask.request.method in ('PUT', 'DELETE', 'PATCH'):
        if not flask.request.if_match:
            raise PreconditionRequired
        if etag not in flask.request.if_match:
            flask.abort(412)
    elif flask.request.method == 'GET':
        if flask.request.if_modified_since:
            last_seen = flask.request.if_modified_since
            last_seen = int(last_seen.strftime("%s"))
            if last_seen >= last_modified:
                raise NotModified
        if flask.request.if_none_match and etag in flask.request.if_none_match:
            raise NotModified

    response = flask.Response(get_file(path), content_type='image/jpeg')
    response.last_modified = last_modified
    response.set_etag(etag)

    return response

class NotModified(HTTPException):
    code = 304
    def get_response(self, environment):
        return flask.Response(status=304)

class PreconditionRequired(HTTPException):
    code = 428
    description = ('<p>This request is required to be '
                   'conditional; try using "If-Match".')
    name = 'Precondition Required'
    def get_response(self, environment):
        resp = super(PreconditionRequired,
                     self).get_response(environment)
        resp.status = str(self.code) + ' ' + self.name.upper()
        return resp