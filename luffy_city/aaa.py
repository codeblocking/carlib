import os

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "luffy_city.settings")
    import django

    django.setup()

    from api import models
    from django.contrib.contenttypes import models as co_model

    # 为django免费课，添加三个价格策略
    #原始方式，比较麻烦
    # course = models.Course.objects.get(pk=1)
    # table_id = co_model.ContentType.objects.get(model='course')
    # ret = models.PricePolicy.objects.create(period=1, price=9.9, course_id=course.pk, table_id=table_id)
    # ret = models.PricePolicy.objects.create(period=7, price=19.9, course_id=course.pk, table_id=table_id)
    # ret = models.PricePolicy.objects.create(period=14, price=29.9, course_id=course.pk, table_id=table_id)
    #

    # contenttype提供的快速插入的方法
    #
    # course = models.Course.objects.get(pk=1)
    # ret=models.PricePolicy.objects.create(period=30, price=199.9,content_obj=course)

    #为学位课，添加一个价格策略
    # degree_course=models.DegreeCourse.objects.get(pk=1)
    # ret = models.PricePolicy.objects.create(period=180, price=28888, content_obj=degree_course)

    # 查询所有价格策略，并且显示对应的课程名称
    # price_policy_list=models.PricePolicy.objects.all()
    # for price_policy in price_policy_list:
    #
    #     print(type(price_policy.content_obj))

        # print(price_policy.content_obj.name)

    # 查询django课程信息的所有价格策略
    # course=models.Course.objects.get(pk=1)
    # #policy_list 就是django这门课所有的价格策略对象
    # policy_list=course.policy.all()
    # for policy in policy_list:
    #     print(policy.price)

    #查询python全栈开发的所有价格策略
    degree_course=models.DegreeCourse.objects.get(pk=1)
    policy_list=degree_course.policy.all()
    for policy in policy_list:
        print(policy.price)


