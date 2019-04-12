from rest_framework.response import Response
from rest_framework.views import APIView
from api import models
from api.utils.commonutils import LuffyResponse
from api.utils.commonutils import CommonException

from api.luffyserializers import Courseserializers
from api.luffyserializers import CoursesDetailSerializers
from rest_framework.viewsets import ViewSetMixin
from django.core.exceptions import ObjectDoesNotExist
import uuid

class LoginView(APIView):

    def post(self, request):
        response=LuffyResponse()
        name = request.data.get('name')
        pwd = request.data.get('pwd')
        try:
            user=models.UserInfo.objects.get(username=name,password=pwd)

            token=uuid.uuid4()
            ret=models.Token.objects.update_or_create(user=user,defaults={'key':token})

            response.token=token
            response.name=name
            response.msg='登录成功'

        except ObjectDoesNotExist as e:
            response.status=101
            response.msg='用户名或密码错误'
        except Exception as e:
            response.status=105
            response.msg=str(e)
        return Response(response.get_dic)
