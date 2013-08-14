#coding=utf8
from django.contrib.auth import get_user_model
from rest_framework import viewsets, serializers, relations

from karma.models import Tweet

User = get_user_model()

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'screen_name', 'twitter_id', 'avatar', 'url']

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    model = User
    queryset = User.public.with_points().order_by('pk')
    serializer_class = UserSerializer

    paginate_by = 50

class TweetSerializer(serializers.HyperlinkedModelSerializer):
    sender = relations.PrimaryKeyRelatedField()
    receiver = relations.PrimaryKeyRelatedField()

    class Meta:
        model = Tweet
        fields = ['id', 'receiver', 'sender', 'amount', 'text', 'twitter_id', 'url']

class TweetViewSet(viewsets.ReadOnlyModelViewSet):
    u"""
    `Tweet` šiuo atveju yra žinutė,
    kuri buvo užskaityta upkarmoas boto
    kaip teisinga ir už ją buvo priskaičiuota
    karmos taškų.

    """
    model = Tweet
    queryset = Tweet.public.all().order_by('pk')
    serializer_class = TweetSerializer

    paginate_by = 50
