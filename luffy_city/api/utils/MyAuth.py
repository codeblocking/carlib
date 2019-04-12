


from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from api import models
class LoginAuth(BaseAuthentication):
    def authenticate(self, request):
        token=request.GET.get('token')

        ret=models.Token.objects.filter(key=token).first()
        if ret:
            return ret.user,token
        else:
            raise AuthenticationFailed('您没有登录，请先登录')