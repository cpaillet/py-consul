from tornado import gen, httpclient

from consul import base

__all__ = ["Consul"]


class HTTPClient(base.HTTPClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = httpclient.AsyncHTTPClient()

    def response(self, response):
        return base.Response(response.code, response.headers, response.body.decode("utf-8"))

    @gen.coroutine
    def _request(self, callback, request):
        try:
            response = yield self.client.fetch(request)
        except httpclient.HTTPError as e:
            if e.code == 599:
                raise base.Timeout
            response = e.response
        raise gen.Return(callback(self.response(response)))

    def get(self, callback, path, params=None):
        uri = self.uri(path, params)
        return self._request(callback, uri)

    def put(self, callback, path, params=None, data=""):
        uri = self.uri(path, params)
        request = httpclient.HTTPRequest(
            uri, method="PUT", body="" if data is None else data, validate_cert=self.verify
        )
        return self._request(callback, request)

    def delete(self, callback, path, params=None):
        uri = self.uri(path, params)
        request = httpclient.HTTPRequest(uri, method="DELETE", validate_cert=self.verify)
        return self._request(callback, request)

    def post(self, callback, path, params=None, data=""):
        uri = self.uri(path, params)
        request = httpclient.HTTPRequest(uri, method="POST", body=data, validate_cert=self.verify)
        return self._request(callback, request)

    def close(self):
        self.client.close()


class Consul(base.Consul):
    def http_connect(self, host, port, scheme, verify=True, cert=None):
        return HTTPClient(host, port, scheme, verify=verify, cert=cert)

    def close(self):
        """Close all opened http connections"""
        return self.http.close()
