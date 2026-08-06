from rest_framework import serializers
from .models import Region, Event, User, Device,Message,PhoneDepartment,PhoneNumber


class EventSerializer(serializers.ModelSerializer):
    user__username = serializers.CharField(source='user.username', read_only=True)
    m_unit = serializers.CharField(source='user.m_unit', read_only=True)
    c_node = serializers.CharField(source='user.communication_node', read_only=True)
    region__name = serializers.CharField(source='region.name', read_only=True)
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    class Meta:
        model = Event
        fields = ['id','theme','user','m_unit','c_node','main_body','comment', 'timestamp', 'region','region__name','user__username']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email','region']


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['name', 'ip_manzili', 'is_active']


class RegionSerializer(serializers.ModelSerializer):
    events = EventSerializer(many=True, read_only=True)
    citizens = UserSerializer(many=True, read_only=True)
    devices = DeviceSerializer(many=True, read_only=True)

    class Meta:
        model = Region
        fields = ['id', 'name', 'events', 'citizens', 'devices']


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.full_name', read_only=True)

    class Meta:
        model = Message
        fields = ['sender', 'text','file', 'created_at']


class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = ['fio','department','panasonic_number','zas_number','grandstream_number','city_number','mobile_number']

class PhoneDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneDepartment
        fields = ['name']