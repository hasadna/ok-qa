import urllib2
import tempfile

from django.core.files.base import ContentFile

from avatar.models import Avatar

def create_avatar(user, url):
    avatar = Avatar(user=user, primary=True)
    image_data = urllib2.urlopen(url).read()
    avatar.avatar.save(tempfile.mktemp(dir='')+'.jpg',
                       ContentFile(image_data))
    avatar.save()

def get_user_avatar(backend, details, response, social_user, uid,\
                    user, *args, **kwargs):
    url = None
    if backend.__class__.__name__ == 'FacebookBackend':
        url = "http://graph.facebook.com/%s/picture?type=large" % response['id']
    elif backend.__class__.__name__ == 'TwitterBackend':
        url = response.get('profile_image_url', '').replace('_normal', '')
    if url:
        create_avatar(user, url)
