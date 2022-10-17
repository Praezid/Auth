from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveUpdateAPIView, get_object_or_404
from authentication.models import User
from authentication.serializers import RegisterSerializer, LoginSerializer, UserSerializer
from rest_framework import response, status, permissions
from django.contrib.auth import authenticate
from notifications.signals import notify


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
        user = authenticate(username=request.data.get('email', None), password=request.data.get('password', None))
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
        user = get_object_or_404(self.get_queryset(), id=self.kwargs["id"])
        if user:
            serializer = self.get_serializer(user)
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response({'message': user}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        user = get_object_or_404(self.get_queryset(), id=self.kwargs["id"])
        serializer = self.get_serializer(user, data=request.data, many=False, partial=True)
        if serializer.is_valid():
            serializer.save()
            notify.send(user, recipient=user, verb='UpDated', description="You updated your account", level='success')
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserNotificationListAPIView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(self.get_queryset(), id=self.kwargs["id"])
        if user:
            if user.notifications.unread().count() == 0:
                return response.Response({'user': request.user.email,
                                          'message': 'User have not notifications'}, status=status.HTTP_200_OK)
            else:
                data = [{'id': item.id,
                         'level': item.level,
                         'description': item.description,
                         'message': str(item)} for item in user.notifications.unread()]
                user.notifications.mark_all_as_read()
                return response.Response({'user': request.user.email, 'notifications': data},
                                         status=status.HTTP_200_OK)
        return response.Response({'message': user}, status=status.HTTP_404_NOT_FOUND)
