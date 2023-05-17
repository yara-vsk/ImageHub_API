import os
from datetime import datetime, timedelta


import pytz
from django.core.signing import Signer
from django.http import FileResponse, Http404, HttpResponse
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ImageHostingAPI.settings import MEDIA_ROOT
from image.fileschecker import files_checker
from image.imagecreator import create_image, create_binary_image
from image.models import Image
from image.serializers import ImageSerializer
from users.models import Tier


class ImageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        images = Image.objects.filter(uploader=user)
        serializer = ImageSerializer(images, many=True, context={'request':request})
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        images_list = []
        files = list(request.data.values())
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
    content = {
        'error': 'Does not exist'
    }

    if path[-1] == "/":
        path = path[:-1]
    image = Image.objects.filter(image__contains=path).first()

    if image:
        if image.uploader != request.user:
            return Response(content)
        height = request.GET.get('height')
        thumbnail_sizes = [str(thumbnail.size) for thumbnail in Tier.objects.get(id=request.user.tier.id).thumbnail_sizes.all()]

        if str(height) not in thumbnail_sizes:
            if not [key for (key, value) in request.GET.items()]:
                response = FileResponse(open(MEDIA_ROOT + '/' + path, 'rb'))
                return response
            return Response(content)
        root = MEDIA_ROOT + '/' + 'user_' + str(request.user.id) + '/' + str(height)

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
    return Response(content)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_signed_url(request):
    signer = Signer()
    signed_image_data = request.GET.get('image_name')

    try:
        image_data = signer.unsign_object(signed_image_data)
    except:
        return Response({'error': 'Url data does not find.'})

    expiry_seconds = request.GET.get('seconds')
    if not expiry_seconds:
        return Response({'error': 'The number of seconds of link activity was not indicated.'})

    try:
        if int(expiry_seconds) < 300 or int(expiry_seconds) > 30000:
            return Response(
                {'error': 'the number of seconds of link activity should be in the range of 300 to 30000 seconds.'})
    except TypeError:
        Response({'error': 'The number of seconds of link activity should be a number.'})

    expiry_time = datetime.now(pytz.utc) + timedelta(seconds=int(expiry_seconds))
    expiry_time_string = expiry_time.strftime('%Y-%m-%d %H:%M:%S')
    image_data.update({'expiry_time': expiry_time_string})
    data_obj = signer.sign_object(image_data)
    url = f'{request.scheme}://{request.get_host()}' + '/api/v1/expiring_link' + '?url=' + str(data_obj)
    return Response({'expiring_link': url})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_image_binary(request):
    signer = Signer()
    signed_image_data = request.GET.get('url')
    if not signed_image_data:
        return Response({'error': 'Signed URL not found in cookie.'})

    try:
        image_data = signer.unsign_object(signed_image_data)
        expiry_time = datetime.strptime(image_data['expiry_time'], '%Y-%m-%d %H:%M:%S')
    except:
        return Response({'error': 'Invalid signed URL.'})

    if expiry_time < datetime.now():
        return Response({'error': 'Link has expired.'})

    image = Image.objects.filter(image__contains=image_data['path']).first()
    path = image_data['path']

    if image:
        if image.uploader != request.user:
            return Response({'error': 'Does not exist'})

        response = create_binary_image(MEDIA_ROOT, path)
        return HttpResponse(response, content_type="image/jpeg")

    return Response({'error': 'Does not exist'})
