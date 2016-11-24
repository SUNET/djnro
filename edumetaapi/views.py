from django.core.urlresolvers import reverse
from django.http.response import HttpResponse, Http404
from rest_framework import permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from edumanage.models import ServiceLoc, Institution
from edumetaapi.serializers import ServiceLocSerializer, InstitutionSerializer


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class LocationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id=None):
        if id:
            try:
                serializer = ServiceLocSerializer(ServiceLoc.objects.get(id=id))
            except ServiceLoc.DoesNotExist as e:
                raise Http404("Location does not exist")
            return JSONResponse(serializer.data)

        institution_id = request.user.userprofile.institution_id
        service_locations = ServiceLoc.objects.filter(institutionid=institution_id)
        serializer = ServiceLocSerializer(service_locations, many=True)
        return JSONResponse(serializer.data)

    def post(self, request):
        request.data['institutionid'] = request.user.userprofile.institution_id
        serializer = ServiceLocSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers={'Location': reverse('location', args=[serializer.data['id']])})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstitutionView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id=None):
        if id:
            try:
                serializer = InstitutionSerializer(Institution.objects.get(id=id))
            except ServiceLoc.DoesNotExist as e:
                raise Http404("Institution does not exist")
            return JSONResponse(serializer.data)

        institution_id = request.user.userprofile.institution_id
        institutions = Institution.objects.get(id=institution_id)
        serializer = InstitutionSerializer(institutions)
        return JSONResponse(serializer.data)
