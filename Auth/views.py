from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from Auth import tasks
from Auth.ml import train_transporter_model
from . import serializers
from . import models
from django.db.models import Avg
from py3dbp import Packer, Bin, Item

class Signup(APIView):
    def post(self, request):
        data = request.data
        user_type = data.get('type')

        if not user_type:
            return Response({'error': 'User type is required (transport or company).'}, status=status.HTTP_400_BAD_REQUEST)

        user_type = user_type.lower()
        if user_type == 'transport':
            ser = serializers.UserTransportSerializer(data=data)
        elif user_type == 'company':
            ser = serializers.UserCompanySerializer(data=data)
        else:
            return Response({'error': 'Invalid user type.'}, status=status.HTTP_400_BAD_REQUEST)

        if ser.is_valid():
            user = ser.save(type=user_type)
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            return Response({
                'user': ser.data,
                'refresh': str(refresh),
                'access': str(access_token)
            }, status=status.HTTP_201_CREATED)

        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

class Login(APIView):
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password')

        if not (name or email) or not password:
            return Response({'error': 'Name or email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = models.User.objects.get(name=name) if name else models.User.objects.get(email=email)
            if not user.check_password(password):
                return Response({'error': 'Incorrect password.'}, status=status.HTTP_401_UNAUTHORIZED)

            serializer = serializers.UserCompanySerializer(user) if user.type == 'company' else serializers.UserTransportSerializer(user)
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(access_token)
            }, status=status.HTTP_200_OK)

        except models.User.DoesNotExist:
            return Response({'error': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)

class addtruck(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        ser = serializers.truckser(data=data)
        if ser.is_valid():
            ser.save()
            user.transport.trucks.add(ser.instance)
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

class deletetruck(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        try:
            truck = models.Truck.objects.get(id=id)
            truck.delete()
            return Response({'message': 'Truck deleted successfully'}, status=status.HTTP_200_OK)
        except models.Truck.DoesNotExist:
            return Response({'error': 'Truck does not exist'}, status=status.HTTP_404_NOT_FOUND)

class finishthetransporteur(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        data = request.data
        ser = serializers.UserTransportSerializer(user, data=data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

class adddriver(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        data = request.data
        ser = serializers.driverserl(data=data)
        if ser.is_valid():
            ser.save()
            ser.instance.transport = user.transport
            ser.instance.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self,request):
        user = request.user
        drivers = models.Drivers.objects.filter(transport=user.transport)
        ser = serializers.driverserl(drivers, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)

class deletedriver(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        email = request.data.get('email')
        try:
            driver = models.Drivers.objects.get(email=email)
            driver.delete()
            return Response({'message': 'Driver deleted successfully'}, status=status.HTTP_200_OK)
        except models.Drivers.DoesNotExist:
            return Response({'error': 'Driver does not exist'}, status=status.HTTP_404_NOT_FOUND)

class addproduct(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.type == 'transport':
            return Response({'error': 'You are not allowed to add products'}, status=status.HTTP_403_FORBIDDEN)
        user = request.user
        data = request.data
        ser = serializers.Produitser(data=data)
        if data['name'] in user.company.produit_set.values_list('name', flat=True):
            amount = user.company.produit_set.get(name=data['name']).amount
            user.company.produit_set.filter(name=data['name']).update(amount=amount + data['amount'])
            ser = serializers.Produitser(user.company.produit_set.get(name=data['name']))
            return Response(ser.data, status=status.HTTP_200_OK)
        if ser.is_valid():
            ser.save()
            user.company.produit_set.add(ser.instance)
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

class sortie(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id):
        user = request.user
        data = request.data
        truck = models.Truck.objects.get(id=id)
        if truck.status == 'Free':
            truck.status = 'Occupied'
            truck.save()
        elif truck.status == 'Occupied':
            truck.status = 'Free'
            truck.save()
        ser = serializers.truckser(truck)
        return Response(ser.data, status=status.HTTP_201_CREATED)

class addfeedback(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        ser = serializers.feedser(data=data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

class RecommendBestTransporterAPIView(APIView):
    def get(self, request):
        desti = request.data.get('destination')
        begin = request.data.get('begin')
        produit = request.data.get('produit')
        amount = request.data.get('amount')
        other = request.data.get('other')
        truck_type = 'van' if other == 'rapid delivery' else 'truck'

        model = train_transporter_model()

        try:
            prod = models.Produit.objects.get(name=produit)
        except models.Produit.DoesNotExist:
            return Response({"error": "Product does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        if model is None:
            return Response({"error": "Not enough feedback data to train the model"}, status=status.HTTP_400_BAD_REQUEST)

        transporters = models.Transport.objects.filter(
            trucks__status='Free',
            road__destination=desti,
            road__begin=begin,
            trucks__type=truck_type,
            trucks__volume__gte=int(amount) * int(prod.volume)
        )

        recommendations = []

        for transporter in transporters:
            feedbacks = models.Feedback.objects.filter(transporter=transporter)

            for truck in transporter.trucks.all():
                truck.percentage = truck.volume / (int(amount) * int(prod.volume))
                truck.save()
                if int(truck.volume) == int(amount) * int(prod.volume):
                    truck.full = True
                    truck.save()

            if feedbacks.exists():
                avg_rating = feedbacks.aggregate(Avg('rating'))["rating__avg"] or 0
                avg_time = feedbacks.aggregate(Avg('delivery_time'))["delivery_time__avg"] or 0

                if avg_rating > 0 and avg_time > 0:
                    predicted_success = model.predict([[avg_rating, avg_time]])[0]
                else:
                    predicted_success = 0

                ser = serializers.TransportSerializer(transporter)

                recommendations.append({
                    "transporter": ser.data,
                    "predicted_success": float(predicted_success),
                    "average_rating": float(avg_rating)
                })

        recommendations = sorted(recommendations, key=lambda x: (-x["predicted_success"], -x["average_rating"]))

        return Response({'recommendation': recommendations}, status=status.HTTP_200_OK)

class addroad(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        ser = serializers.roadser(data=data)
        if ser.is_valid():
            ser.save()
            user.transport.road_set.add(ser.instance)
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

class deleteroad(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        try:
            road = models.Road.objects.get(id=id)
            road.delete()
            return Response({'message': 'Road deleted successfully'}, status=status.HTTP_200_OK)
        except models.Road.DoesNotExist:
            return Response({'error': 'Road does not exist'}, status=status.HTTP_404_NOT_FOUND)

class RecommendBestTransporterSharedAPIView(APIView):
    def get(self, request):
        desti = request.data.get('destination')
        begin = request.data.get('begin')
        produit = request.data.get('produit')
        amount = request.data.get('amount')
        other = request.data.get('other')

        truck_type = 'van' if other == 'rapid delivery' else 'default_type'

        model = train_transporter_model()

        try:
            prod = models.Produit.objects.get(name=produit)
        except models.Produit.DoesNotExist:
            return Response({"error": "Product does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        if model is None:
            return Response({"error": "Not enough feedback data to train the model"}, status=status.HTTP_400_BAD_REQUEST)

        transporters = models.Transport.objects.filter(
            shared_trucks__status='Free',
            road__destination=desti,
            road__begin=begin,
            shared_trucks__type=truck_type,
            shared_trucks__volume__gte=int(amount) * int(prod.volume)
        )

        recommendations = []

        for transporter in transporters:
            feedbacks = models.Feedback.objects.filter(transporter=transporter)

            for shared_truck in transporter.shared_trucks.all():
                shared_truck.percentage = shared_truck.volume / (int(amount) * int(prod.volume))
                shared_truck.save()
                if int(shared_truck.volume) == int(amount) * int(prod.volume):
                    shared_truck.full = True
                    shared_truck.save()

            if feedbacks.exists():
                avg_rating = feedbacks.aggregate(Avg('rating'))["rating__avg"] or 0
                avg_time = feedbacks.aggregate(Avg('delivery_time'))["delivery_time__avg"] or 0

                if avg_rating > 0 and avg_time > 0:
                    predicted_success = model.predict([[avg_rating, avg_time]])[0]
                else:
                    predicted_success = 0

                ser = serializers.TransportSerializer(transporter)

                recommendations.append({
                    "transporter": ser.data,
                    "predicted_success": float(predicted_success),
                    "average_rating": float(avg_rating)
                })

        recommendations = sorted(recommendations, key=lambda x: (-x["predicted_success"], -x["average_rating"]))

        return Response({'recommendation': recommendations}, status=status.HTTP_200_OK)
class findtime(APIView):
    def post(self,request):
        pass
class OptimizeSpace(APIView):
    def get(self, request,id):
        # Step 1: Define the Truck (Container)
        try:
         tr= models.Truck.objects.get(id=id)
        except models.Truck.DoesNotExist:
            return Response({'user dosent exist'},status=status.HTTP_404_NOT_FOUND)
        products=request.data.get('produits')
        truck = Bin('Truck', width=tr.width, height=tr.height, depth=500, max_weight=tr.maxweight)

        # Step 2: Define Boxes with Quantities
        for pr in products:
            product=models.Produit.objects.get(name=pr['name'])
            box_data = [
                {"name": product.name, "width": product.width, "height": product.height, "depth": 100, "weight": product.weight, "quantity": pr['amount'], "fragile": product.type=='Fragile'},
            ]

        # Step 3: Initialize the Packer
        packer = Packer()
        packer.add_bin(truck)

        # Step 4: Sort Items (Fragile items are added last)
        sorted_boxes = sorted(box_data, key=lambda x: x["fragile"])

        # Step 5: Add Boxes to the Packer (Based on Quantity)
        for box in sorted_boxes:
            for _ in range(box["quantity"]):  # Add each item separately
                packer.add_item(
                    Item(
                        name=box["name"],
                        width=box["width"],
                        height=box["height"],
                        depth=box["depth"],
                        weight=box["weight"]
                    )
                )

        # Step 6: Run the Packing Algorithm
        packer.pack()

        # Step 7: Prepare Response Data
        packed_boxes = []
        for b in packer.bins:
            for item in b.items:
                packed_boxes.append({
                    "name": item.name,
                    "position": item.position,  # Position (x, y, z)
                    "layer": item.position[1],  # Y-axis represents the layer
                })

        return Response({"message": "Space optimized", "boxes": packed_boxes}, status=status.HTTP_200_OK)
