from rest_framework.response import Response
from rest_framework.views import APIView
from api import models
from api.utils.commonutils import LuffyResponse
from api.utils.commonutils import CommonException

from api.luffyserializers import Courseserializers
from api.luffyserializers import CoursesDetailSerializers
from rest_framework.viewsets import ViewSetMixin
from django.core.exceptions import ObjectDoesNotExist
class CourseView(ViewSetMixin,APIView):

    def get_list(self, request, *args, **kwargs):
        response = LuffyResponse()
        try:
            category=int(request.GET.get('category',None))
            course_list = models.Course.objects.all()

            if category:
                course_list=course_list.filter(course_category_id=category)

            course_ser = Courseserializers(instance=course_list, many=True)

            response.data = course_ser.data

        except Exception as e:
            response.status = 105
            response.msg = str(e)
            # response.msg = '您的操作有误'

        return Response(response.get_dic)

    #单个课程详情接口
    def get_detail(self, request, pk):
        response = LuffyResponse()
        try:
            #注意：用course_id来查询
            course_detail=models.CourseDetail.objects.get(course_id=pk)
            course_detail_ser=CoursesDetailSerializers(instance=course_detail,many=False)

            response.data=course_detail_ser.data
            response.msg='查询成功'

        except ObjectDoesNotExist as e:
            response.status = 101
            response.msg = '课程不存在'
        except Exception as e:
            response.status = 105
            response.msg = str(e)
            # response.msg = '您的操作有误'

        return Response(response.get_dic)

