from rest_framework.generics import GenericAPIView, RetrieveAPIView, UpdateAPIView, RetrieveUpdateAPIView, \
    get_object_or_404

from authentication.models import User
from authentication.serializers import RegisterSerializer, LoginSerializer, UserSerializer
from rest_framework import response, status, permissions
from django.contrib.auth import authenticate


class RegisterApiView(GenericAPIView):
    authentication_classes = []

    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(GenericAPIView):
    authentication_classes = []

    serializer_class = LoginSerializer

    def post(self, request):
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        user = authenticate(username=email, password=password)
        if user:
            serializer = self.serializer_class(user)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        return response.Response({'message': 'Invalid credentials, try again'}, status=status.HTTP_401_UNAUTHORIZED)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        id = self.kwargs["id"]
        user = get_object_or_404(self.get_queryset(), id=id)
        if user:
            serializer = self.get_serializer(user)
            return response.Response(serializer.data, status=status.HTTP_200_OK)

        return response.Response({'message': '404 error. Detail not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        data = request.data
        id = self.kwargs["id"]
        user = get_object_or_404(self.get_queryset(), id=id)
        serializer = self.get_serializer(user, data=data, many=False, partial=True)

        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)

        return response.Response({'message': '400 error. Bad request'}, status=status.HTTP_400_BAD_REQUEST)
