from django.core.signing import Signer
from rest_framework import serializers
from image.models import Image


class ImageSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['id','name','links']


    def get_links(self, obj):
        links = {}
        request = self.context['request']
        tier = request.user.tier
        scheme_host_name=f'{request.scheme}://{request.get_host()}'
        thumbnail_sizes = tier.thumbnail_sizes.split(',')
        try:
            thumbnail_sizes = [int(x) for x in thumbnail_sizes]
        except ValueError:
            thumbnail_sizes = []
            links['error_thumbnail_sizes'] = 'Comma-separated list of thumbnail heights.'
        if tier.link_originally_image:
            links['link_originally_image'] = scheme_host_name + obj.image.url
        if tier.expiring_links:
            signer = Signer()
            signed_url = signer.sign_object({'path': obj.image.name})
            links['expiring_link'] = scheme_host_name + '/api/v1/create_expiring_link' + '?image_name=' + signed_url + '&seconds='
        for height in thumbnail_sizes:
            name_thumbnail = 'thumbnail_' + str(height) + '_link'
            links[name_thumbnail] = scheme_host_name + obj.image.url + '?height=' + str(height)
        return links

    def get_name(self, obj):
        return str(obj.image.name).split('/')[-1]


