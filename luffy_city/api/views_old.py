from django.shortcuts import render

# Create your views here.
from rest_framework.views import  APIView
from rest_framework.response import Response
class Course(APIView):
    def get(self,request):

        return Response(['python课程', 'linux', 'go语言','dasfdasfdasf'])