from django.utils.deprecation import MiddlewareMixin


class MyMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # 处理了简单请求
        response['Access-Control-Allow-Origin'] = '*'
        # 处理非简单请求
        if request.method == 'OPTIONS':
            response['Access-Control-Allow-Headers'] = '*'
            # response['Access-Control-Allow-Methods']='PUT,PATCH'
            response['Access-Control-Allow-Methods'] = '*'

        return response
