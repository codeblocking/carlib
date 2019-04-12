from rest_framework import serializers
from api import models


class Courseserializers(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = '__all__'

    price = serializers.SerializerMethodField()

    def get_price(self, obj):
        price_policy = obj.price_policy.all().order_by('-price').first()
        return price_policy.price


class PolicyPriceSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.PricePolicy
        fields = ['price', 'valid_period', 'valid_per_display']

    # valid_per_display=serializers.CharField(source='get_valid_period_display')
    valid_per_display = serializers.SerializerMethodField()

    def get_valid_per_display(self, obj):
        return obj.get_valid_period_display()


class CoursesDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.CourseDetail
        fields = '__all__'

    # 取出课程的所有价格策略
    policy_price_list = serializers.SerializerMethodField()

    def get_policy_price_list(self, obj):
        policy_list = obj.course.price_policy.all()
        # policy_ser=PolicyPriceSerializers(instance=policy_list,many=True)
        # return policy_ser.data

        return [{'id': policy.pk, 'valid_per_display': policy.get_valid_period_display(),'price':policy.price} for policy in policy_list]

    course_name=serializers.CharField(source='course.name')

    teachers=serializers.SerializerMethodField()
    def get_teachers(self,obj):
        teacher_list=obj.teachers.all()

        return [{'id':teacher.pk,'name':teacher.name}  for teacher in teacher_list]

