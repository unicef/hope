from flags.state import flag_enabled
from silk.middleware import SilkyMiddleware


class DynamicSilkyMiddleware(SilkyMiddleware):
    def __call__(self, request):
        if flag_enabled("SILK_MIDDLEWARE", request=request):
            self.process_request(request)
            response = self.get_response(request)
            response = self.process_response(request, response)
        else:
            response = self.get_response(request)

        return response
