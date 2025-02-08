from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, Company, Produit, Drivers, Transport, Truck, road,track,Feedback,sharedtruckes

class trackser(serializers.ModelSerializer):
    class Meta:
        model = track
        fields = '__all__'

class driverserl(serializers.ModelSerializer):
    class Meta:
        model = Drivers
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class Produitser(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'
class feedser(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
class truckser(serializers.ModelSerializer):
    class Meta:
        model = Truck
        fields = ['name', 'height','width','status','type','full','percentage','weight']
class sharedtruckser(serializers.ModelSerializer):
    class Meta:
        model = sharedtruckes
        fields = ['name','height','width','status','type','full','percentage']

class UserCompanySerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    password = serializers.CharField(write_only=True)
    type = serializers.CharField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'number', 'company', 'type', 'date_joined', 'password']

    def create(self, validated_data):
        company_data = validated_data.pop('company', None)
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        company = Company.objects.create(**company_data)
        user.company = company
        user.save()
        return user

    def update(self, instance, validated_data):
        company_data = validated_data.pop('company', None)
        instance = super().update(instance, validated_data)

        if company_data is not None:
            if instance.company:
                company_serializer = CompanySerializer(
                    instance=instance.company,
                    data=company_data,
                    partial=self.partial
                )
                company_serializer.is_valid(raise_exception=True)
                company_serializer.save()
            else:
                instance.company = Company.objects.create(**company_data)
                instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        company_representation = representation.pop('company', None)
        if company_representation:
            representation.update(company_representation)  # Merge company data
        return representation
class roadser(serializers.ModelSerializer):
    class Meta:
        model = road
        fields = '__all__'
class TransportSerializer(serializers.ModelSerializer):
    driver = driverserl(required=False)
    trucks = truckser(many=True,required=False)
    road=roadser(required=False)

    class Meta:
        model = Transport
        fields = ['id', 'driver', 'trucks','road']

    def create(self, validated_data):
        trucks_data = validated_data.pop('trucks', None)
        transport = Transport.objects.create(**validated_data)
        if trucks_data:
            for truck_data in trucks_data:
                truck = Truck.objects.create(**truck_data)
                transport.trucks.add(truck)
        return transport

    def update(self, instance, validated_data):
        trucks_data = validated_data.pop('trucks', None)
        instance = super().update(instance, validated_data)
        if trucks_data:
            for truck_data in trucks_data:
                truck_serializer = truckser(data=truck_data, partial=self.partial)
                truck_serializer.is_valid(raise_exception=True)
                truck = truck_serializer.save()
                instance.trucks.add(truck)
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        driver_representation = representation.pop('driver', None)
        trucks_representation = representation.pop('trucks', None)
        if driver_representation:
            representation.update(driver_representation)  # Merge driver data
        if trucks_representation:
            representation.update({'trucks': trucks_representation})  # Merge trucks data
        return representation

class UserTransportSerializer(serializers.ModelSerializer): 
    password = serializers.CharField(write_only=True)
    transport = TransportSerializer()
    type = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'transport','number', 'type', 'date_joined', 'password']

    def create(self, validated_data):
        transport_data = validated_data.pop('transport', None)
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        if transport_data:
            trucks=transport_data.pop('trucks')
            transport = Transport.objects.create(**transport_data)
            for truck in trucks:
             truc=Truck.objects.create(**truck)
             transport.trucks.add(truc)
             transport.save()
            user.transport = transport
            user.save()
        return user

    def update(self, instance, validated_data):
        transport_data = validated_data.pop('transport', None)
        instance = super().update(instance, validated_data)

        if transport_data is not None:
            if instance.transport:
                transport_serializer = TransportSerializer(
                    instance=instance.transport,
                    data=transport_data,
                    partial=self.partial
                )
                transport_serializer.is_valid(raise_exception=True)
                transport_serializer.save()
            else:
                instance.transport = Transport.objects.create(**transport_data)
                instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        transport_representation = representation.pop('transport', None)
        if transport_representation:
            representation.update(transport_representation)  # Merge transport data
        return representation