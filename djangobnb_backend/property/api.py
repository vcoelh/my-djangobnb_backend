from django.http import JsonResponse

from rest_framework.decorators import api_view, authentication_classes, permission_classes

from .models import Property, Reservation
from .forms import PropertyForm
from .serializers import PropertiesListSerializer, PropertiesDetailsSerializer, ReservationsListSerializer

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def properties_list(request):
    properties = Property.objects.all()
    
    landlord_id = request.GET.get('landlord_id', '')
    
    if landlord_id:
        properties = properties.filter(landlord_id=landlord_id)
    
    serializer = PropertiesListSerializer(properties, many=True)
    
    return JsonResponse({
        'data': serializer.data
    })


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def properties_detail(request, pk):
    property = Property.objects.get(pk=pk)
    
    serializer = PropertiesDetailsSerializer(property, many=False)
    
    return JsonResponse(serializer.data)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
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

    
