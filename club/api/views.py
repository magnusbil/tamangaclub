from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, permissions
import json
from django.contrib.auth.models import User
from knox.models import AuthToken
from club.models import UserProfile, Series, Book, Poll, Choice, Vote, SharedAccess
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer, PollSerializer, SeriesSerializer, BookSerializer, SharedAccessSerializer

class RegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        data = json_loads(request.body.decode(encoding="utf-8"))
        user_data = {"username": data['username'], "password": data['password']}
        serializer = self.get_serializer(data=request.data) # HAVE TO UPDATE THIS
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        #SET SECURITY QUESTION AND ANSWER
        user.UserProfile.security_question = data['security_question']
        user.UserProfile.security_answer = data['seurity_answer']
        user.UserProfile.save()

        return JsonResponse({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return JsonResponse({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })

def password_reset(request):
  if request.method == 'POST':
    try:
      data = json.loads(request.body.decode(encoding='utf-8'))
      user = User.objects.get(username=data['username'])
      if data['answer'] == user.secret:
        new_password = make_password(data['password'])
        user.password = new_password
        user.save()
        return JsonRepsonse({
          "user": UserSerializer(user, context=self.get_serializer_context()).data,
          "token": AuthToken.objects.create(user)[1]
        })
    except(e):
      error_message = str(e)
      return JsonRepsonse){"error_message":error_message, status=400}

def get_security_question(request):
  return

def validate_security_answer(request):
  return

@permission_classes([permissions.IsAuthenticated])
class UserAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

@permission_classes([permissions.IsAuthenticated])
class BooksListView(ListAPIView):
  queryset = Book.objects.all()
  serializer_class = BookSerializer

@permission_classes([permissions.IsAuthenticated])
class BooksBySeriesListView(ListAPIView):
  queryset = Book.objects.all()
  serializer_class = BookSerializer
  lookup_field = 'series'

@permission_classes([permissions.IsAuthenticated])
class PollListView(ListAPIView):
  queryset = Poll.objects.all()
  serializer_class = PollSerializer

@permission_classes([permissions.IsAuthenticated])
class RecentBooksView(ListAPIView):
  queryset = Book.objects.all()[:8]
  serializer_class = BookSerializer

@permission_classes([permissions.IsAuthenticated])
class SeriesListView(ListAPIView):
  queryset = Series.objects.all()
  serializer_class = SeriesSerializer

@permission_classes([permissions.IsAuthenticated])
class SeriesByTitleDetailView(RetrieveAPIView):
  queryset = Series.objects.all()
  serializer_class = SeriesSerializer
  lookup_field = 'series_title'

@permission_classes([permissions.IsAuthenticated])
class SharedAccessListView(ListAPIView):
  queryset = SharedAccess.objects.all()
  serializer_class = SharedAccessSerializer

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def vote(request):
  try:
    request_data = json.loads(request.body.decode(encoding='utf-8'))
    votes = Vote.objects.filter(user=request_data['user_id'], poll=request_data['poll_id'])
    if len(votes) == 0:
      user = User.objects.get(id=request_data['user_id'])
      poll = Poll.objects.get(id=request_data['poll_id'])
      choice = Choice.objects.get(id=request_data['choice_id'])
      vote = Vote.objects.create(user=user,poll=poll,choice=choice)
      vote.save()
      choice_total_votes = Vote.objects.filter(choice=choice).count()
      poll_total_votes = Vote.objects.filter(poll=poll).count()
      result_data = {
        'choice_total_votes': choice_total_votes,
        'poll_total_votes': poll_total_votes
      }
      return JsonResponse(result_data)
    else:
      return JsonResponse({"message": "You have already voted on this poll."})
  except Exception as e:
    error_message = str(e)
    return JsonResponse({"error_message":error_message}, status=400)
