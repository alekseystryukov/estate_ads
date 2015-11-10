from django.template import Library, Node
from ads.models import Ad



register = Library()


@register.tag
def get_blocked_ads(parser, token):

    return BlockedAdsNode()


class BlockedAdsNode(Node):
    def render(self, context):
        context['blocked_ads'] = Ad.objects.all().filter(blocked=None)
        return ''