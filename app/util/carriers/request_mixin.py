import requests


class RequestMixin(object):
    def send_request(self, method, url, params=None, payload=None):
        response = requests.request()
        return response

    def _get_config(self):
        pass