import os
from datetime import datetime, timedelta
import pytz
from django.core.exceptions import ObjectDoesNotExist
from django.core.signing import Signer, BadSignature
from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ImageHostingAPI.settings import MEDIA_ROOT
from image.fileschecker import files_checker
from image.imagecreator import create_image
from image.models import Image
from image.serializers import ImageSerializer
from users.models import Tier


error_cont_404 = {'error': 'Does not exist'}


class ImageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        images = Image.objects.filter(uploader=user)
        serializer = ImageSerializer(images, many=True, context={'request':request})
        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        images_list = []
        files = list(request.FILES.values())
        if not files:
            return Response({'error': "HTTP request does not contain image(s)."},
                            status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if files_checker(files):
            for image in files:
                image = Image.objects.create(
                    image=image,
                    uploader=user
                )
                images_list.append(image)
            serializer = ImageSerializer(images_list, many=True, context={'request':request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': "Image(s) should be in the format PNG or JPG."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def media_access(request, path, *args, **kwargs):
    user = request.user

    try:
        image = Image.objects.get(image__exact=path)
    except ObjectDoesNotExist:
        return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)

    if image.uploader != user:
        return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)

    height = str(request.GET.get('height'))
    thumbnail_sizes = [str(thumbnail.size) for thumbnail in
                       Tier.objects.get(id=request.user.tier.id).thumbnail_sizes.all()]

    if height not in thumbnail_sizes:
        if not [key for key in request.GET.keys()] and user.tier.link_originally_image:
            response = FileResponse(open(MEDIA_ROOT + '/' + path, 'rb'))
            return response
        return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)

    root = MEDIA_ROOT + '/' + 'user_' + str(user.id) + '/' + height

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_signed_url(request):
    signer = Signer()
    signed_image_data = request.GET.get('image_name')
    expiry_seconds = request.GET.get('seconds')

    if not request.user.tier.expiring_links:
        return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)

    if signed_image_data is None or expiry_seconds is None:
        return Response({'error': "Parameter 'image_name' or / and 'seconds' are missing in the request"},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        image_data = signer.unsign_object(signed_image_data)
    except BadSignature:
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
    url = f'{request.scheme}://{request.get_host()}'+'/api/v1/expiring_link'+'?url='+signer.sign_object(image_data)
    return Response({'expiring_link': url})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_image_binary(request):
    signer = Signer()
    signed_image_data = request.GET.get('url')

    if not request.user.tier.expiring_links:
        return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)

    if signed_image_data is None:
        return Response({'error': "Parameter 'url' is missing in the request"},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        image_data = signer.unsign_object(signed_image_data)
    except BadSignature:
        return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)

    expiry_time = datetime.strptime(image_data['expiry_time'], '%Y-%m-%d %H:%M:%S.%f%z')

    if expiry_time < datetime.now(pytz.utc):
        return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)

    path = image_data['path']
    image = Image.objects.filter(image__contains=path).first()

    if image:
        if image.uploader != request.user:
            return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)
        response = FileResponse(open(MEDIA_ROOT + '/' + path, 'rb'))
        return response

    return Response(error_cont_404, status=status.HTTP_404_NOT_FOUND)



