from rest_framework.response import Response
from rest_framework.views import APIView
from api import models
from api.utils.commonutils import LuffyResponse
from api.utils.commonutils import CommonException

from api.luffyserializers import Courseserializers
from api.luffyserializers import CoursesDetailSerializers
from rest_framework.viewsets import ViewSetMixin
from django.core.exceptions import ObjectDoesNotExist

from django_redis import get_redis_connection

import json
from api.utils.MyAuth import LoginAuth

#购物车需要登录之后才能操作（认证组件）
class ShoppingView(APIView):
    authentication_classes=[LoginAuth]
    conn=get_redis_connection()
    def post(self,request):
        response=LuffyResponse()
        try:
            course_in_id=request.data.get('course_id')
            policy_in_id=request.data.get('policy_id')
            # 1 查询课程是否存在
            course=models.Course.objects.get(pk=course_in_id)
            #2 获取所有价格策略
            policy_list=course.price_policy.all()
            #3 取出当前用户购物车的数据
            shopping_cart_dic_bytes=self.conn.get('shopping_card_%s'%request.user.id)
            #json可以loadsbytes格式
            shopping_cart_dic=json.loads(shopping_cart_dic_bytes) if shopping_cart_dic_bytes else {}

            # if shopping_cart_dic_bytes:
            #     shopping_cart_dic=json.loads(shopping_cart_dic_bytes)
            # else:
            #     shopping_cart_dic={}

            #4 循环价格策略
            policy_dict={}
            for policy in policy_list:
                policy_dict[str(policy.pk)]={
                    'period':policy.valid_period,
                    'period_display':policy.get_valid_period_display(),
                    'price':policy.price

                }
            #5 校验价格策略是否是该课程的价格策略
            if policy_in_id not in policy_dict:
                raise CommonException('你是爬虫，价格策略不合法')
            #6 构造购物车的字典
            # shopping_cart_dic[str(course.pk)]
            shopping_cart_dic[course_in_id]={
                'title':course.name,
                'img':course.course_img,
                'default_policy':policy_in_id,
                'policy':policy_dict
            }
            #7 存入redis
            self.conn.set('shopping_card_%s'%request.user.id,json.dumps(shopping_cart_dic))
            response.msg='加入购物车成功'

        except CommonException as e:
            response.status = 102
            response.msg = e.msg
        except ObjectDoesNotExist as e:
            response.status = 101
            response.msg = '您要加入购物车的课程不存在'
        except Exception as e:
            response.status=105
            response.msg=str(e)
        return Response(response.get_dic)

    def get(self,request):
        response = LuffyResponse()
        shopping_cart_dic_bytes = self.conn.get('shopping_card_%s' % request.user.id)
        shopping_cart_dic = json.loads(shopping_cart_dic_bytes) if shopping_cart_dic_bytes else {}
        response.data=shopping_cart_dic
        response.msg='查询成功'

        return Response(response.get_dic)

    def delete(self,request):
        #传入的数据格式{"course_id":"1"}
        course_in_id=request.data.get('course_id')
        response = LuffyResponse()
        shopping_cart_dic_bytes = self.conn.get('shopping_card_%s' % request.user.id)
        shopping_cart_dic = json.loads(shopping_cart_dic_bytes) if shopping_cart_dic_bytes else {}
        shopping_cart_dic.pop(course_in_id)
        #保存到redis中
        self.conn.set('shopping_card_%s' % request.user.id, json.dumps(shopping_cart_dic))
        response.msg = '删除成功'
        return Response(response.get_dic)

    def put(self,request):

        course_in_id=request.data.get('course_id')
        policy_in_id=request.data.get('policy_id')
        response = LuffyResponse()
        try:
            shopping_cart_dic_bytes = self.conn.get('shopping_card_%s' % request.user.id)
            shopping_cart_dic = json.loads(shopping_cart_dic_bytes) if shopping_cart_dic_bytes else {}
            #取出该课程所有的价格策略
            policy=shopping_cart_dic[course_in_id]['policy']
            if policy_in_id not in policy:
                raise CommonException('传入的价格策略非法，你可能是爬虫')
            shopping_cart_dic[course_in_id]['default_policy']=policy_in_id

            #保存到redis中
            self.conn.set('shopping_card_%s' % request.user.id, json.dumps(shopping_cart_dic))
            response.msg='修改成功'

        except CommonException as e:
            response.status = 102
            response.msg = e.msg
        except Exception as e:
            response.status=105
            response.msg=str(e)
        return Response(response.get_dic)