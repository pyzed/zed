# -*- coding: utf-8 -*-

from rest_framework import serializers
from models import API, RunScripts, UserData,ReturnLog


class APISerializer(serializers.ModelSerializer):
    class Meta:
        model = API
        fields = ('ssh_host', 'ssh_port', 'ssh_user', 'ssh_pass')


class RunScriptsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RunScripts
        fields = '__all__'


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = '__all__'

class ReturnLogSerializer(serializers.ModelSerializer):
    class Meta:
	model = ReturnLog
	fields = '__all__'
