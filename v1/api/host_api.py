# -*- coding: utf-8 -*-

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework.decorators import list_route

from models import API
from serializers import APISerializer
from v1.utils.GetPublicKey import ReturnHostsResult
from v1.utils import Users
import os
import commands
import json

class AddOneHosts(APIView):
    """
    从后台新增一台主机信息，获取信息第一次登录，复制id_rsa.pub至主机
    """

    def get(self, request):
        """
        get请求
        :param request:
        :return:
        """
        api = API.objects.all()
        serializer = APISerializer(api, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        post请求
        :param request:
        :return:
        """
        # serializer = APISerializer(data=request.data)
        # if serializer.is_valid():
        print request.data
        rd = ReturnHostsResult(request.data).main()
        print type(rd)
        if not rd:
            return Response(rd, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(rd, dict) and rd.get('code') != 200:
            return Response(rd, status=status.HTTP_400_BAD_REQUEST)
        return Response(rd, status=status.HTTP_201_CREATED)
        # return Response(result['message'], status=status.HTTP_400_BAD_REQUEST)

class UsersPostSsh(APIView):
    def post(self,request):
        data = request.data
        try:
            if not request.data:
                return Response({"code": 4040, "message": 'No data available'}, status=status.HTTP_404_NOT_FOUND) 
            print data
            user_list = Users.ExistsUser(data).get_users()
            return Response(user_list, status=status.HTTP_200_OK)
        except Exception as e:
            print e
            return Response({"code": 4040, "message": e}, status=status.HTTP_404_NOT_FOUND)



class UsersPostSsh(APIView):
    """
    用户相关操作
    """
    def post(self,request):
        """
        """
        data = request.data
        try:
            if not request.data:
                return Response({"code": 4040, "message": 'No data available'}, status=status.HTTP_404_NOT_FOUND)
            print data
            post_user_list = Users.ExistsUser(data).get_users()
            return Response(post_user_list, status=status.HTTP_200_OK)
        except Exception as e:
            print e
            return Response({"code": 4040, "message": e}, status=status.HTTP_404_NOT_FOUND)


class UsersGetList(APIView):
    """
    """
    def post(self,request):
        try:
            if not request.data:
                return Response({"code": 4040, "message": 'No data available'}, status=status.HTTP_404_NOT_FOUND)
            data = request.data
            print data
            user_list = Users.ExistsUser(data).get_users_list()
            return Response(user_list, status=status.HTTP_200_OK)
        except Exception as e:
            print e
            return Response({"code": 4040, "message": e}, status=status.HTTP_404_NOT_FOUND)

class UsersProfile(APIView):
    """用户相关操作"""
    def get(self,request):
        """
        返回主机当前用户，不包含root(在每次结果里添加？)
        :param request:
        :return:
        """
        try:
            if not request.GET:
                return Response({"code": 4040, "message": 'No data available'}, status=status.HTTP_404_NOT_FOUND)
            data = request.GET
            print data
            user_list = Users.ExistsUser(data).get_users()
            return Response(user_list, status=status.HTTP_200_OK)
        except Exception as e:
            print e
            return Response({"code": 4040, "message": e}, status=status.HTTP_404_NOT_FOUND)

    def post(self,request):
        """
        添加用户
        :param request:
        :return:
        """
        data = request.data
        print data
        try:
            result = Users.AddUser(data).create_user()
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            print e
            return Response({"code": 4040, "message": e}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        """
        删除用户
        :param request:
        :return:
        """
        data = request.data
        print data
        try:
            result = Users.DeleteUser(data).del_user()
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            print e
            return Response({"code": 4040, "message": e}, status=status.HTTP_404_NOT_FOUND)
