#encoding=utf8
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import AbstractBaseUser

from .utils import get_global_client, get_week_start
from .exceptions import SenderBanned, ReceiverBanned

class User(AbstractBaseUser):
    screen_name = models.CharField('Twitter screen name', unique=True,
                                   max_length=255)
    twitter_id = models.CharField('Twitter id', max_length=255)
    avatar = models.URLField('Twitter avatar URL', blank=True)
    banned = models.BooleanField('Boolean showing if user is banned',
        default=0,
        null=False,
    )
    # denormalized field for storing the point amount
    points = models.IntegerField(default=0)

    # django auth thingies
    USERNAME_FIELD = 'screen_name'
    REQUIRED_FIELDS = ['twitter_id']

    @classmethod
    def from_twitter_id(cls, twitter_id):
        """
        Given a user's twitter_id, creates a User,
        prefilled with info from his twitter account,
        saves and returns it
        """
        u = cls()
        tw = get_global_client()

        info = tw.users.show(user_id=twitter_id)
        u.screen_name = info['screen_name']
        u.avatar = info['profile_image_url']

        u.save()

        return u

    def get_limit_usage(self, receiver=None):
        """
        Gets User's point sending limit usage
        If receiver is not none, also gets the usage
        for the specific receiver
        """
        usage = {}
        base_qs = self.karma_sends.filter(date__gte=get_week_start())
        usage['per_week'] = base_qs.aggregate(s=Sum('amount'))['s'] or 0

        if receiver is not None:
            qs = base_qs.filter(receiver=receiver)
            usage['per_week_receiver'] = qs.aggregate(s=Sum('amount'))['s'] or 0

        return usage

class Tweet(models.Model):
    """
    A Tweet, giving some karma points
    """

    sender = models.ForeignKey(
        User,
        null=True,
        related_name='karma_sends',
        on_delete=models.SET_NULL
    )
    receiver = models.ForeignKey(
        User,
        null=True,
        related_name='karma_receives',
        on_delete=models.SET_NULL
    )
    amount = models.IntegerField('Amount of points')
    date = models.DateTimeField()
    twitter_id = models.CharField('Twitter id of the tweet', max_length=255)

    text = models.TextField(blank=True)


    def clean(self):
        # ban checks
        if self.sender.banned:
            raise SenderBanned(u'Jūs buvote pašalintas iš žaidimo.')
        if self.receiver.banned:
            raise ReceiverBanned(u'Vartotojas, kuriam siunčiate karmos'
                    u' buvo pašalintas iš žaidimo')

        # amount check
        amounts = settings.UPKARMA_SETTINGS['valid_amount_range']

        if self.amount < amounts[0] or self.amount > amounts[1]:
            msg = (u'Netinkamas taškų kiekis. Viena žinute galima' \
                  u' duoti nuo {0} iki {1} tšk.').format(*amounts)
            raise ValidationError(msg)

        self.clean_limits()

    def clean_limits(self):
        usage = self.sender.get_limit_usage(receiver=self.receiver)
        limits = settings.UPKARMA_SETTINGS['limits']

        left = limits['per_week'] - usage['per_week']
        if left < self.amount:
            msg = (u'Nepakankamas savaitės taškų limitas.' \
                  u' Šią savaitę jums liko {0} tšk.').format(left)
            raise ValidationError(msg)

        left = limits['per_week_receiver'] - usage['per_week_receiver']

        if left < self.amount:
            msg = (u'Nepakankamas savaitės taškų limitas šiam asmeniui.' \
                   u' Šią savaitę jam dar galite duoti {0} tšk.').format(left)
            raise ValidationError(msg)


    def save(self, skip_checks=False, **kwargs):
        """
        skip_checks is required when restoring a dump
        because of limits filling up
        """
        if not skip_checks:
            self.full_clean()

        super(Tweet, self).save(**kwargs)

    def __str__(self):
        return '{0} points @{1} -> @{2}'.format(self.amount,
                                                self.sender,
                                                self.receiver)
