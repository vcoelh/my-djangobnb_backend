from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.tokens import AccessToken

from .models import Property, Reservation
from .forms import PropertyForm
from .serializers import PropertiesListSerializer, PropertiesDetailsSerializer, ReservationsListSerializer
from useraccount.models import User

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def properties_list(request):
    #
    # Auth
    if request.user.is_authenticated:
        print('Logged in as:', request.user.email)
    else:
        print('User is anonymous')
    
    #
    #
    favorites = []
    properties = Property.objects.all()

    
    #
    # Filter
    is_favorites = request.GET.get('is_favorites', '')
    landlord_id = request.GET.get('landlord_id', '')
    
    if is_favorites:
        properties = properties.filter(favorited__in=[request.user])
    
    if landlord_id:
        properties = properties.filter(landlord_id=landlord_id)
    
    
    #
    # Favoroties
    if request.user.is_authenticated:
        for property in properties:
            if request.user in property.favorited.all():
                favorites.append(property.id)
    
    print(f'{favorites=}')
    #
    #
    
    serializer = PropertiesListSerializer(properties, many=True)
    
    return JsonResponse({
        'data': serializer.data,
        'favorites': favorites,
    })


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def properties_detail(request, pk):
    property = Property.objects.get(pk=pk)
    
    serializer = PropertiesDetailsSerializer(property, many=False)
    
    return JsonResponse(serializer.data)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def property_reservations(request, pk):
    property = Property.objects.get(pk=pk)
    reservations = property.reservations.all()
    
    serializer = ReservationsListSerializer(reservations, many=True)
    
    return JsonResponse(serializer.data, safe=False)
    
    
    
@api_view(['POST', 'FILES'])
def create_property(request):
    form = PropertyForm(request.POST, request.FILES)
    
    if form.is_valid():
        property = form.save(commit=False)
        property.landlord = request.user
        property.save()
        
        return JsonResponse({'success': True})
    else:
        print('error', form.errors, form.non_field_errors)
        return JsonResponse({'errors': form.errors.as_json()}, status=400)



@api_view(['POST'])
def book_property(response, pk):
    try:
        start_date = response.POST.get('start_date', '')
        end_date = response.POST.get('end_date', '')
        number_of_nights = response.POST.get('number_of_nights', '')
        total_price = response.POST.get('total_price', '')
        guests = response.POST.get('guests', '')
        
        property = Property.objects.get(pk=pk)
        
        Reservation.objects.create(
            property=property,
            start_date=start_date,
            end_date=end_date,
            number_of_nights=number_of_nights,
            total_price=total_price,
            guests=guests,
            created_by=response.user
        )
        
        return JsonResponse({'success': True})
    except Exception as e:
        print('Error', e)
    
        return JsonResponse({'success': False})
    
@api_view(['POST'])
def toggle_favorite(request, pk):
    property = Property.objects.get(pk=pk)
    
    if request.user in property.favorited.all():
        property.favorited.remove(request.user)
    
        return JsonResponse({'is_favorite': False})
    else:
        property.favorited.add(request.user)
        
        return JsonResponse({'is_favorite': True})
        

    
