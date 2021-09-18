from uuid import uuid4

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from django.core.exceptions import ObjectDoesNotExist

from server.model.ca import CA
from server.serializer.ca import CASerializer
from server.views.mixins import SessionMixin


class CACreate(SessionMixin, GenericAPIView):
    queryset = CA.objects.all()
    serializer_class = CASerializer
    # TODO: list endpoint

    def post(self, request, *args, **kwargs):
        uuid = uuid4()
        ca = CA(uuid=uuid)
        ca.save()
        self.create_sessions(uuid, request.data["timeSlots"])
        return Response(data={"uuid": str(uuid)}, status=status.HTTP_200_OK)


class CAItem(APIView, SessionMixin):
    def get(self, request, ca_id, *args, **kwargs):
        try:
            ca = CA.objects.filter(id__exact=ca_id).get()
            data = CASerializer(ca).data
        except ObjectDoesNotExist:
            return Response(data={}, status=status.HTTP_404_NOT_FOUND)
        data["timeSlots"] = self.get_sessions(ca.uuid)

    def put(self, request, ca_id, *args, **kwargs):
        try:
            ca = CA.objects.filter(id__exact=ca_id).get()
        except ObjectDoesNotExist:
            return Response(data={}, status=status.HTTP_404_NOT_FOUND)

        # TODO: Make difflist instead
        ca.name = request.data["name"]
        ca.description = request.data["description"]
        student_limit = 1
        if "studentLimit" in request.data:
            student_limit = request.data["name"]

        self.deletion_sessions(ca_id)
        self.create_sessions(ca_id, student_limit, request.data["timeSlots"])
        return Response(data={"uuid": str(ca_id)}, status=status.HTTP_200_OK)

    def delete(self, request, ca_id, *args, **kwargs):
        try:
            CA.objects.filter(id__exact=ca_id).delete()
        except ObjectDoesNotExist:
            return Response(data={}, status=status.HTTP_404_NOT_FOUND)

        self.deletion_sessions(ca_id)
        return Response(data={"uuid": str(ca_id)}, status=status.HTTP_200_OK)