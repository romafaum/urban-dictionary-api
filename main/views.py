from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from main.serializer import DefinitionSerializer
from main.helper_func import (
    get_definitions,
    get_author_definitions,
    get_random_definitions
)




@csrf_exempt
def definitions_view(request, name):
    """ Definition view """
    if request.method == "GET":
        objects = get_definitions(name)
        serializer = DefinitionSerializer(objects, many=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def author_view(request, name):
    """ Author view """
    if request.method == "GET":
        objects = get_author_definitions(name)
        serializer = DefinitionSerializer(objects, many=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def random_view(request):
    """ Random view """
    if request.method == "GET":
        objects = get_random_definitions()
        serializer = DefinitionSerializer(objects, many=True)
        return JsonResponse(serializer.data, safe=False)