
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
import datetime
import json
from api.utils.MyAuth import LoginAuth
import time
#结算中心
class PaymentView(APIView):
    conn=get_redis_connection()
    authentication_classes=[LoginAuth]
    def post(self,request):
        #{"course_list":[{"course_id":"1","policy_id":"1"},{"course_id":"2","policy_id":"2"}]}
        response = LuffyResponse()
        course_in_list=request.data.get('course_list')
        try:
            # 1 定义结算中心的字典，定义全局优惠券的字典
            payment_dict_userid = {}
            global_coupon_dict = {
                "coupon": {},
                "default_coupon": 0
            }
            #2 拿到购物车，循环取出传入的课程id，判断是否在购物车中，不在直接抛异常
            shopping_cart_dic_bytes = self.conn.get('shopping_card_%s' % request.user.id)
            # json可以loadsbytes格式
            shopping_cart_dic = json.loads(shopping_cart_dic_bytes) if shopping_cart_dic_bytes else {}
            for course_in in course_in_list:
                course_in_id=course_in.get('course_id')
                if course_in_id not in shopping_cart_dic:
                    raise CommonException('要结算的课程不合法，不在购物车中')
                #3 构造单个课程详情的字典，把购物车中的当前课程，update到该字典中
                course_detail = {
                    'coupon': {},
                    'default_coupon':'0'
                    #....课程详情的数据
                }
                course_detail.update(shopping_cart_dic[course_in_id])
                #4 将该课程详情，加入到结算中心
                payment_dict_userid[course_in_id]=course_detail
            #5 一次性查出当前用户的所有优惠券信息（用户为当前用户，状态为未使用，优惠券起始时间小于当前时间，优惠券结束时间大于当前时间）
            #获取当前时间
            ctime = datetime.datetime.today().strftime('%Y-%m-%d')
            print(ctime)
            #查询此人所有可用优惠券
            coupon_list = models.CouponRecord.objects.filter(
                user=request.user,
                status=0,
                coupon__valid_begin_date__lte=ctime,
                coupon__valid_end_date__gte=ctime,
            )
            #6 循环所有优惠券
            for item in coupon_list:
                #7 构造出单个优惠券的空字典，拿到优惠券类型（1立减 2 满减 3折扣），拿到优惠券id，拿到该优惠券绑定的课程id（有可能为空）
                coupon_detail = {}
                #优惠券类型
                coupon_type=item.coupon.coupon_type
                #优惠券id
                coupon_id=item.pk
                #该优惠券绑定的课程id(根据这个字段判断是全站优惠券还是课程优惠券)
                course_id=item.coupon.object_id
                #8 构造单个优惠券字典，将数据填充进去
                coupon_detail['coupon_type'] = coupon_type
                coupon_detail['coupon_display'] = item.coupon.get_coupon_type_display()
                if coupon_type == 0:  # 立减券，构造出等值金额
                    coupon_detail['money_equivalent_value'] = item.coupon.money_equivalent_value
                elif coupon_type == 1:  # 满减券，构造出等值金额，和最低消费金额
                    coupon_detail['money_equivalent_value'] = item.coupon.money_equivalent_value
                    coupon_detail['minimum_consume'] = item.coupon.minimum_consume
                else:  # 其他情况，构造出打折（如打八折，80）
                    coupon_detail['off_percent'] = item.coupon.off_percent

                #9 判断是全站优惠券还是课程优惠券
                if not course_id:
                        #课程id为空，放到全站优惠券大字典中
                        global_coupon_dict['coupon'][str(coupon_id)]=coupon_detail
                else:
                    #课程优惠券
                    coupon_course_id = str(course_id)
                    if coupon_course_id not in payment_dict_userid:  # 当前课程优惠券对应的可能如果不在结算中心字典里，continue
                        continue
                    # 在结算中心字典中的，对应放入到课程优惠券字段上
                    payment_dict_userid[str(coupon_course_id)]['coupon'][str(coupon_id)] = coupon_detail


            # 10讲结算中心字典和全局优惠券字典，放入redis中
            self.conn.set('payment_dict_%s'%request.user.id,json.dumps(payment_dict_userid))
            self.conn.set('global_coupon_dict_%s'%request.user.id,json.dumps(global_coupon_dict))
            response.msg='加入结算中心成功'


        except CommonException as e:
            response.status = 102
            response.msg = e.msg
        except Exception as e:
            response.status = 105
            response.msg = str(e)
        return Response(response.get_dic)

    def get(self,request):
        response=LuffyResponse()
        payment_dic_bytes=self.conn.get('payment_dict_%s'%request.user.id)
        global_coupon_dict_bytes=self.conn.get('global_coupon_dict_%s'%request.user.id)
        payment_dic= json.loads(payment_dic_bytes)  if payment_dic_bytes else {}
        global_coupon_dict= json.loads(global_coupon_dict_bytes)  if global_coupon_dict_bytes else {}
        response.msg='查询成功'
        response.data={
            'payment':payment_dic,
            'global_coupon':global_coupon_dict
        }
        return Response(response.get_dic)



class PayFinal(APIView):
    conn=get_redis_connection()
    authentication_classes=[LoginAuth]
    def post(self,request):
        #传入的数据格式
        # {
        #     "price": 600
        #     "bely": 100
        # }
        response = LuffyResponse()

        try:
            price_in = request.data.get('price')
            bely = request.data.get('bely')
            #1从结算中心拿出字典,全局优惠券字典取出来
            payment_dic_bytes=self.conn.get('payment_dict_%s' % request.user.id)
            payment_dic=json.loads(payment_dic_bytes)  if payment_dic_bytes else {}
            global_coupon_dic_bytes=self.conn.get('payment_dict_%s' % request.user.id)
            global_coupon_dic=json.loads(global_coupon_dic_bytes)  if global_coupon_dic_bytes else {}

            price_list=[]
            #2 循环结算中心字典，得到课程和课程id
            for course_id,course_detail in payment_dic.items():
                # 3取出默认价格策略，取出默认价格，取出默认优惠券id
                default_policy_id=course_detail['default_policy']
                default_price=course_detail['policy'][default_policy_id]['price']
                default_coupon_id=course_detail['default_coupon']
                #4 判断如果默认优惠券不为0，
                # 表示使用了优惠券：
                # 取出默认优惠券的字典，
                # 调用计算价格函数得到价格，把价格放到价格列表中（后面直接用sum函数计算总价格）
                if default_coupon_id!=0:
                    #使用了优惠券
                    default_coupon_detail=course_detail['coupon'][default_coupon_id]
                    #调用计算价格的函数
                    default_price=self.account(default_price,default_coupon_detail)
                price_list.append(default_price)
            #5 取出全局默认优惠券id，根据默认优惠券id取出全局优惠券字典，调用计算价格函数得到实际支付价格
            global_coupon_id=global_coupon_dic['default_coupon']
            if global_coupon_id!=0:
                global_coupon_detail=global_coupon_dic['coupon'][str(global_coupon_id)]
                final_price=self.account(sum(price_list),global_coupon_detail)
            else:
                final_price=sum(price_list)

            #6判断贝利数大于传入的贝利数，
            # 用实际价格减去贝利数，如果得到结果小于0，
            # 直接等于0，判断最终价格和传如的价格是否相等，
            # 不相等抛异常
            if not request.user.beli>=bely:
                raise CommonException('贝利数不合法')
            final_price=final_price-bely/10
            if final_price<0:
                final_price=0

            if final_price !=price_in:
                raise CommonException('传入的价格不合法')
            if final_price>0:
                #构造支付宝支付
                # 拼凑支付宝url
                alipay = ali()
                # 生成支付的url
                query_params = alipay.direct_pay(
                    subject="路飞学成课程",  # 商品简单描述
                    out_trade_no="x2" + str(time.time()),  # 商户订单号
                    total_amount=final_price,  # 交易金额(单位: 元 保留俩位小数)
                )
                pay_url = "https://openapi.alipaydev.com/gateway.do?{}".format(query_params)
                response.url = pay_url


        except CommonException as e:
            response.status = 102
            response.msg = e.msg
        except Exception as e:
            response.status = 105
            response.msg = str(e)
        return Response(response.get_dic)


    def account(self,price,coupon_dic):
        # 设置总价格为price
        total_price = price
        # 取出优惠券类型
        coupon_type = coupon_dic['coupon_type']
        # 优惠券类型是0，立减
        if coupon_type == 0:
            total_price = price - coupon_dic['money_equivalent_value']

        ##优惠券类型是1，满减，必须大于最低消费金额
        elif coupon_type == 1:
            if price >= coupon_dic['minimum_consume']:
                total_price = price - coupon_dic['money_equivalent_value']
            else:
                raise CommonException('优惠券不满足最低使用金额')
        ##优惠券类型是2，直接打折
        elif coupon_type == 2:
            total_price = price * coupon_dic['off_percent'] / 100

        return total_price
