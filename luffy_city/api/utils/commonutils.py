

#公共响应
class LuffyResponse():
    def __init__(self):
        self.status='100'
        self.msg=None
        self.data=None
    @property
    def get_dic(self):
        return self.__dict__

#公共异常类
class CommonException(Exception):
    def __init__(self,msg):
        self.msg=msg