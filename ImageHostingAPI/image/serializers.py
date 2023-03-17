from django.core.signing import Signer
from rest_framework import serializers
from image.models import Image
from users.models import Tier


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
        thumbnail_sizes = list(Tier.objects.get(id=tier.id).thumbnail_sizes.all())
        if tier.link_originally_image:
            links['link_originally_image'] = scheme_host_name + obj.image.url
        if tier.expiring_links:
            signer = Signer()
            signed_url = signer.sign_object({'path': obj.image.name})
            links['expiring_link'] = scheme_host_name + '/api/v1/create_expiring_link' + '?image_name=' + signed_url + '&seconds='
        for thumbnail in thumbnail_sizes:
            name_thumbnail = 'thumbnail_' + str(thumbnail.size) + '_link'
            links[name_thumbnail] = scheme_host_name + obj.image.url + '?height=' + str(thumbnail.size)
        return links

    def get_name(self, obj):
        return str(obj.image.name).split('/')[-1]


