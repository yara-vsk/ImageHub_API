import os
import re
from datetime import datetime, timedelta
import pytz
from django.core.signing import Signer, BadSignature
from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ImageHostingAPI.settings import MEDIA_ROOT
from image.imagecreator import create_image
from image.models import Image
from image.serializers import ImageSerializer
from users.models import Tier


error_cont_404 = {'error': 'Does not exist'}


class ImageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        images = Image.objects.filter(uploader=request.user)
        serializer = ImageSerializer(images, many=True, context={'request':request})
        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        max_file_size = 10 * 1024 * 1024
        file_list = list(request.FILES.values())
        user = request.user

        if not file_list or len(file_list) > 1:
            return Response({'error': "The HTTP request should contain one image."},
                            status=status.HTTP_400_BAD_REQUEST)

        image_file = file_list[0]

        if re.match(r'.*\.(png|jpg)$', image_file.name) and image_file.size <= max_file_size:
            image = Image.objects.create(
                image=image_file,
                uploader=user
            )

            serializer = ImageSerializer(image, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({'error': "Image should be in the format PNG or JPG. Maximum file size: 10 MB"},
                        status=status.HTTP_400_BAD_REQUEST)


class ImageDownloadAPIView(APIView):

    def get(self, request, *args, **kwargs):
        signer = Signer()
        signed_image_data = request.GET.get('image_data')

        if signed_image_data is None:
            return Response({'error': "Parameter 'image_data' is missing in the request"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            image_data = signer.unsign_object(signed_image_data)
        except BadSignature:
            return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)

        path = image_data['path']
        expiry_time_str = image_data.get('expiry_time')
        height = image_data.get('height')

        if expiry_time_str is None and height is None:
            return self.get_originally_image(path)
        elif height:
            return self.get_thumbnail(height, path)
        elif expiry_time_str == 'default':
            return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)

        return self.get_originally_image_by_exp_link(expiry_time_str, path)


    def get_originally_image(self, path):
        image = Image.objects.filter(image__contains=path).first()

        if image.uploader.tier.link_originally_image:
            response = FileResponse(open(MEDIA_ROOT + '/' + path, 'rb'))
            return response

        return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)


    def get_thumbnail(self, height, path):
        image = Image.objects.filter(image__contains=path).first()
        thumbnail_sizes = [str(thumbnail.size) for thumbnail in
                           Tier.objects.get(id=image.uploader.tier.id).thumbnail_sizes.all()]

        if height not in thumbnail_sizes:
            return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)

        root = MEDIA_ROOT + '/' + 'user_' + str(image.uploader.id) + '/' + height

        try:
            os.mkdir(root)
            create_image(MEDIA_ROOT, root + '/' + path.split('/')[-1], path, height)
            response = FileResponse(open(root + '/' + path.split('/')[-1], 'rb'))
            return response
        except FileExistsError:
            root = root + '/' + path.split('/')[-1]
            try:
                response = FileResponse(open(root, 'rb'))
                return response
            except FileNotFoundError:
                create_image(MEDIA_ROOT, root, path, height)
                response = FileResponse(open(root, 'rb'))
                return response


    def get_originally_image_by_exp_link(self, expiry_time_str, path):
        expiry_time = datetime.strptime(expiry_time_str, '%Y-%m-%d %H:%M:%S.%f%z')

        if expiry_time < datetime.now(pytz.utc):
            return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)

        image = Image.objects.filter(image__contains=path).first()

        if image:
            response = FileResponse(open(MEDIA_ROOT + '/' + path, 'rb'))
            return response

        return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_expiring_link(request):
    signer = Signer()
    signed_image_data = request.GET.get('image_data')
    expiry_seconds = request.GET.get('seconds')

    if signed_image_data is None or expiry_seconds is None:
        return Response({'error': "Parameter 'image_name' or / and 'seconds' are missing in the request"},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        image_data = signer.unsign_object(signed_image_data)
    except BadSignature:
        return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)

    path = image_data['path']
    expiry_time_str = image_data.get('expiry_time')

    if expiry_time_str != "default":
        return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)


    image = Image.objects.filter(image__contains=path).first()

    if not image.uploader.tier.expiring_links or request.user.id != image.uploader.id:
        return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)

    try:
        expiry_seconds = int(expiry_seconds)
        if expiry_seconds < 300 or expiry_seconds > 30000:
            return Response(
                {'error': 'the number of seconds of link activity should be in the range of 300 to 30000 seconds.'},
                status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({'error': 'The number of seconds of link activity should be a number.'},
                        status=status.HTTP_400_BAD_REQUEST)

    expiry_time = datetime.now(pytz.utc) + timedelta(seconds=expiry_seconds)
    image_data.update({'expiry_time': expiry_time.strftime('%Y-%m-%d %H:%M:%S.%f%z')})
    url = f'{request.scheme}://{request.get_host()}'+'/api/v1/download/'+'?image_data='+signer.sign_object(image_data)
    return Response({'expiring_link': url})