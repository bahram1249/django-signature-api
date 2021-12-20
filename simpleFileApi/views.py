from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .convertor import *
from pathlib import Path


class FileViews(APIView):
    def post(self, request):
        if "file" in request.FILES:
            my_file = request.FILES["file"]
            fs = FileSystemStorage()
            filename = fs.save(generate_uuid() + Path(my_file.name).stem, my_file)
            # uploaded_file_url = fs.url(filename)
            return_file_path = os.path.join(MEDIA_ROOT, process_image(filename))
            return_file = fs.open(return_file_path)
            return_data = return_file.read()
            return_file.close()

            # os.remove(return_file_path)

            return HttpResponse(return_data, status=status.HTTP_200_OK, content_type="image/png")
        else:
            return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)
