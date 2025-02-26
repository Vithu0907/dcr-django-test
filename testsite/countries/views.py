from django.http import JsonResponse
from django.db.models import Count, Sum
from .models import Region

def stats(request: object) -> JsonResponse:
    """
    Statistics about regions and countries.

    Args:
        request (object): The request object.
    
    Returns:
        JsonResponse: A JSON response containing all regions with their names,
                     number of countries, and total population.
    """
    try:
        regions_data = Region.objects.annotate(
            number_countries=Count('countries'),
            total_population=Sum('countries__population')
        ).values('name', 'number_countries', 'total_population')
        
        regions_list = list(regions_data)
        for region in regions_list:
            region['number_countries'] = region['number_countries'] or 0
            region['total_population'] = region['total_population'] or 0
        
        response = {"regions": regions_list}
        return JsonResponse(response)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in stats view: {str(e)}")
        
        return JsonResponse({"error": "An error occurred processing your request"}, status=500)