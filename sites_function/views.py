import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404,render
from rest_framework import status
from django.contrib.auth.models import User
from sites_function.description_filter import strip_html, truncate_words
from sites_function.models import SitesFormat
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from sites_function.serializers import SitesFormatSerializer


@api_view(['POST'])
def register_user(request):
    print("Request data:", request.data) 
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username:
        return Response({"error": "Username must be provided"}, status=status.HTTP_400_BAD_REQUEST)

    if not password:
        return Response({"error": "Password must be provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not email:
        return Response({"error": "email must be provided"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = get_user_model().objects.create_user(username=username, password=password, email=email)
        user.save()

        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        print("Error creating user:", str(e))
        return Response({"error": "An error occurred while creating the user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
@api_view(['POST'])
def login_user(request):
    # print(request.data)
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        if '@' in username:
            user = User.objects.get(email=username)
        else:
            user = User.objects.get(username=username)

    except User.DoesNotExist:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(password):
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

    refresh = RefreshToken.for_user(user)

    return Response({
        'username': user.username,
        'email': user.email,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def google_login(request):
    access_token = request.data.get('access_token')

    if not access_token:
        return Response({"error": "Access token required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_data = requests.get(f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}').json()
        email = user_data.get('email')
        username = user_data.get('name')

        User = get_user_model()
        user, created = User.objects.get_or_create(email=email, defaults={'username': username})

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

    except MissingBackend:
        return Response({"error": "Invalid backend"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def homepage(request):
    frontend_url = os.getenv('FRONTEND_URL')
    print("Frontend URL:", frontend_url)  
    context = {
        'frontend_url': os.getenv('frontend_url'),  # Pass the database URL to the template
        # other context variables...
    }
    return render(request,'homepage.html',context=context)


@api_view(['POST'])
def create_site(request):
    email = request.data.get('email')
    title = request.data.get('title')
    json_content = request.data.get('jsoncontent')
    html_content = request.data.get('htmlcontent')

    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    site = SitesFormat(
        user=user,
        title=title,
        jsoncontent=json_content,
        htmlcontent=html_content
    )
    site.save()

    serializer = SitesFormatSerializer(site)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def user_all_sites(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_sites = SitesFormat.objects.filter(user=user,private=False)

    
    return render(request, 'user_sites_list.html', {'user_sites': user_sites, 'user': user})

def sitesview(request, uuid):
    sites_html_content = get_object_or_404(SitesFormat, id=uuid)

    if sites_html_content.private:
        message = 'This site is private and cannot be accessed.'
        return render(request, 'sites_format.html', {
            'message': message,
            'sites_html_content': None, 
        })
    
    if sites_html_content.is_expired():
        message = 'This site is no longer available.'
        return render(request, 'sites_format.html', {
            'message': message,
            'sites_html_content': None, 
        })
    
    stripped_html = strip_html(sites_html_content.htmlcontent)
    truncated_description = truncate_words(stripped_html, word_count=30)

    return render(request, 'sites_format.html', {
        'sites_html_content': sites_html_content,
        'truncated_description': truncated_description,
        'message': None,
    })

def search_site(request):
    site_id = request.GET.get('query')
    site_html_content = get_object_or_404(SitesFormat, id=site_id)

    return render(request, 'sites_format.html', {'sites_html_content': site_html_content})

def share_site(request, uuid):
    site = get_object_or_404(SitesFormat, id=uuid)

    if site.private:
        site.shared_at = timezone.now()
        site.save()

    return JsonResponse({'shared_id': str(site.id)})

@api_view(['DELETE'])
def delete_site(request,id):
    try:
        site = SitesFormat.objects.get(id=id)
        site.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except SitesFormat.DoesNotExist:
        return Response({'error': 'Site not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def get_user_sites(request):
    email = request.data.get('email')
    try: 
        if not email:
            return JsonResponse({'error': 'email is required'}, status=400)

        user = get_object_or_404(User, email=email)
        user_sites = SitesFormat.objects.filter(user=user)
        data = {
            'user_sites': list(user_sites.values())
            }
        return JsonResponse(data, status=200)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
def get_site_by_id(request):
    id = request.data.get('id')
    
    if not id or not id[0]:
        return JsonResponse({'error': 'id is required'}, status=400)

    try: 
        site = get_object_or_404(SitesFormat, id=id)
        user_id = site.user.id if site.user else None
        data = {
                'user_sites': {
                    'id': site.id, 
                    'user_id': user_id,
                    'user_mail': site.user.email,
                    'title': site.title,
                    'jsoncontent': site.jsoncontent,
                    'htmlcontent': site.htmlcontent,
                    'date_time': site.date_time.isoformat(),
                    'private': site.private,
                    'shared_at': site.shared_at.isoformat() if site.shared_at else None
                }
            }
        return JsonResponse(data, status=200)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
@api_view(['PUT'])
def edit_site(request, id):
    try:
        site = SitesFormat.objects.get(id=id)
    except SitesFormat.DoesNotExist:
        return Response({'error': 'Site not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SitesFormatSerializer(site, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    