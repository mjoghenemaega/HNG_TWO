from rest_framework import status, views, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Organisation
from .serializers import UserSerializer, OrganisationSerializer
from rest_framework.views import APIView

class RegisterView(views.APIView):
    def post(self, request):
        data = request.data
        required_fields = ['firstName', 'lastName', 'email', 'password']

        for field in required_fields:
            if not data.get(field):
                return Response({
                    "errors": [{"field": field, "message": f"{field} is required"}]
                }, status=422)

        if User.objects.filter(email=data.get('email')).exists():
            return Response({
                'status': 'Bad request',
                'message': 'Registration unsuccessful',
                'statusCode': 400,
                "errors": [{"field": "email", "message": "Email already exists"}]
            }, status=400)

        user = User.objects.create_user(
            firstName=data['firstName'],
            lastName=data['lastName'],
            email=data['email'],
            password=data['password'],
            phone=data.get('phone')
        )
        
        organisation = Organisation.objects.create(
            name=f"{data['firstName']}'s Organisation"
        )
        organisation.users.add(user)

        refresh = RefreshToken.for_user(user)
        return Response({
            "status": "success",
            "message": "Registration successful",
            "data": {
                "accessToken": str(refresh.access_token),
                "user": UserSerializer(user).data
            }
        }, status=201)

class LoginView(views.APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return Response({
                "errors": [{"field": "general", "message": "Email and password are required"}]
            }, status=422)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "status": "Bad request",
                "message": "Authentication failed",
                "statusCode": 401
            })

        if not user.check_password(password):
            return Response({
                "status": "Bad request",
                "message": "Authentication failed",
                "statusCode": 401
            })

        refresh = RefreshToken.for_user(user)
        return Response({
            "status": "success",
            "message": "Login successful",
            "data": {
                "accessToken": str(refresh.access_token),
                "user": UserSerializer(user).data
            }
        }, status=200)

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'userId'

class OrganisationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Retrieve organisations belonging to the authenticated user
        user = request.user
        organisations = Organisation.objects.filter(users=user)
        serializer = OrganisationSerializer(organisations, many=True)
        return Response({
            'status': 'success',
            'message': 'Organisations retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = OrganisationSerializer(data=request.data)
        if serializer.is_valid():
            organisation = serializer.save(users=[request.user])
            return Response({
                'status': 'success',
                'message': 'Organisation created successfully',
                'data': OrganisationSerializer(organisation).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "Bad Request",
            "message": "Client error",
            "statusCode": 400,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class OrganisationDetailView(generics.RetrieveAPIView):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'orgId'



class AddUserToOrganisationView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, orgId):
        user_id = request.data.get('userId')
        try:
            user = User.objects.get(userId=user_id)
            organisation = Organisation.objects.get(orgId=orgId)
            organisation.users.add(user)
            return Response({
                "status": "success",
                "message": "User added to organisation successfully",
            }, status=200)
        except User.DoesNotExist:
            return Response({
                "status": "Bad request",
                "message": "User not found",
                "statusCode": 400
            })
        except Organisation.DoesNotExist:
            return Response({
                "status": "Bad request",
                "message": "Organisation not found",
                "statusCode": 400
            })
