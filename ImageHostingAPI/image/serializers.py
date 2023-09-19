from django.core.signing import Signer
from rest_framework import serializers
from image.models import Image
from users.models import Tier


class ImageSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['id','links']


    def get_links(self, obj):
        links = {}
        request = self.context['request']
        tier = request.user.tier
        scheme_host_name = f'{request.scheme}://{request.get_host()}' + '/api/v1/'
        url = 'download?image_data='
        thumbnail_sizes = list(Tier.objects.get(id=tier.id).thumbnail_sizes.all())
        signer = Signer()
        if tier.link_originally_image:
            signed_url = signer.sign_object({'path': obj.image.name})
            links['link_originally_image'] = scheme_host_name + url + signed_url
        if tier.expiring_links:
            signed_url = signer.sign_object({'path': obj.image.name})
            links['expiring_link'] = scheme_host_name + 'create_expiring_link?image_data=' + signed_url + '&seconds='
        for thumbnail in thumbnail_sizes:
            name_thumbnail = 'thumbnail_' + str(thumbnail.size) + '_link'
            signed_url = signer.sign_object({'path': obj.image.name, 'height': str(thumbnail.size)})
            links[name_thumbnail] = scheme_host_name + url + signed_url
        return links



