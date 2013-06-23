#encoding=utf8
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import AbstractBaseUser

from twitter import TwitterHTTPError

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

    def save(self, **kwargs):
        self.solve_screen_name_clashes()

        super(User, self).save(**kwargs)

    def solve_screen_name_clashes(self):
        """
        This method helps avoid screen name clashes
        in situations like:
            1. We have a user with Twitter ID 1 and screen name `guy1`
               and another with ID 2 and screen name `guy2`
            2. ID 2 changes his username to `donkey`
            3. ID 1 changes his username to `guy2`
            4. We update ID 1's info... Oops, there's already a `guy2`!

        This method helps us solve those cases
        by searching users with the same screen name
        at the time we save this user
        and updating their info first,
        thus freeing the name.
        """
        try:
            u = User.objects.exclude(pk=self.pk).get(screen_name=self.screen_name)
        except User.DoesNotExist:
            # no user by our name, carry on
            return
        else:
            try:
                u.fill_info_from_twitter()
            except TwitterHTTPError as e:
                if e.e.getcode() == 404:
                    # well, user has been deleted
                    u.delete()
            else:
                u.save()


    def fill_info_from_twitter(self, twitter_id=None):
        """
        Fills user info from twitter.
        Suitable for updating screen names, avatars,
        also creating new accounts

        This is useful as a general function
        in other use cases than User.from_twitter_id()
        """
        if not twitter_id:
            twitter_id = self.twitter_id
        tw = get_global_client()
        info = tw.users.show(user_id=twitter_id)

        self.screen_name = info['screen_name']
        self.avatar = info['profile_image_url']


    @classmethod
    def from_twitter_id(cls, twitter_id):
        """
        Given a user's twitter_id, creates a User,
        prefilled with info from his twitter account,
        saves and returns it
        """
        u = cls()
        u.fill_info_from_twitter(twitter_id)
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
