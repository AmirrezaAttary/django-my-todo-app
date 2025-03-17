from rest_framework import generics
from accounts.api.v1.serializers import (RegistrationSerializer ,CustomAuthTokenSerializer ,
                                        CustomTokenObtainSerializer, ChangePasswordSerializer,
                                        ProfileSerializer, ActivationResendSerializer)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from accounts.models import Profile
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from mail_templated import EmailMessage
from accounts.api.utils import EmailThread
import jwt
from jwt.exceptions import ExpiredSignatureError,InvalidSignatureError,DecodeError

from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings



User = get_user_model()


class RegistrationAPIView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            email = serializer.validated_data['email']
            data = {
                'email':email
            }
            user_obj = get_object_or_404(User,email=email)
            token = self.get_tokens_for_user(user_obj)
            email_obj = EmailMessage('email/activation_email.tpl', {'token': token}, 'admin@admin.com',to=[email])
            EmailThread(email_obj).start()
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        
    
    def get_tokens_for_user(self,user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

class ObtainAuthTokenView(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
        
class CustomDiscardAuthToken(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request,):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
    



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainSerializer



class ChangePasswordApiView(generics.GenericAPIView):
    model = User
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset):
        obj = self.request.user
        return obj


    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data = request.data)
        
        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get('old_password')):
                return Response({'old_password':["Wrong password."]} , status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get('new_password'))
            self.object.save()
            return Response({'detail':'password change successfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class ProfileApiView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset , user=self.request.user)
        return obj
    
class TestEmailSend(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        self.email = "amir@amir.com"
        user_obj = get_object_or_404(User,email=self.email)
        token = self.get_tokens_for_user(user_obj)
        email_obj = EmailMessage('email/hello.tpl', {'token': token}, 'admin@admin.com',to=[self.email])
        EmailThread(email_obj).start()
        return Response({'detail':'email sent successfully'},status=status.HTTP_200_OK)
    
    def get_tokens_for_user(self,user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    
    
class ActivationApiView(APIView):
    def get(self,request,token,*args,**kwargs):
        try:
            token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = token['user_id']
        except ExpiredSignatureError:
            return Response({'detail':'Activation link has been expired'},status=status.HTTP_400_BAD_REQUEST)
        except InvalidSignatureError:
            return Response({'detail':'Invalid token'},status=status.HTTP_400_BAD_REQUEST)
        except DecodeError:
            return Response({'detail':'Invalid token'},status=status.HTTP_400_BAD_REQUEST)
        
        user_obj = User.objects.get(pk=user_id)
        if user_obj.is_verified:
            return Response({'detail':'your account already verified'},status=status.HTTP_200_OK)
        user_obj.is_verified = True
        user_obj.save()
        return Response({'detail':'your account verification'},status=status.HTTP_200_OK)
    
class ResendActivationEmailApiView(generics.GenericAPIView):
    serializer_class = ActivationResendSerializer
    
    def post(self,request,*args,**kwargs):
        serializer = ActivationResendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.validated_data['user']
        token = self.get_tokens_for_user(user_obj)
        email_obj = EmailMessage('email/activation_email.tpl', {'token': token}, 'admin@admin.com',to=[user_obj.email])
        EmailThread(email_obj).start()
        return Response({'detail':'email sent successfully'},status=status.HTTP_200_OK)
                
        
    def get_tokens_for_user(self,user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)