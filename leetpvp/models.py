from django.db import models
from django.contrib.auth.models import User
import json, requests
from datetime import datetime
import threading, time

from eveonline.models import EveCharacter, EveCorporationInfo

# Create your models here.


class KbStat(models.Model):
    shipsDestroyed = models.IntegerField(default=0)
    shipsLost = models.IntegerField(default=0)

    year = models.TextField()
    month = models.TextField()

    iskDestroyed = models.BigIntegerField(default=0)
    iskLost = models.BigIntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User)

    url = 'https://zkillboard.com/api/stats/characterID/'

    def get_character_stats(self, characterId):
        url = self.url + characterId
        resp = requests.get(url=url)
        data = json.loads(resp.text)
        # for key, stat in data['months'].iteritems():
        #     kbstat = KbStat()
        #     kbstat.year = stat['year']
        #     kbstat.month = stat['month']
        #     kbstat.shipsDestroyed = stat['shipsDestroyed']
        #     kbstat.shipsLost = stat['shipsLost']

        return data.get('months')

    def get_corp_stats(self):
        for user in User.objects.all():
            self.get_user_stats(user=user)

    def get_user_characters(self, user):
        characters = EveCharacter.objects.filter(user=user)
        return characters

    def get_user_stats(self, user):
        KbStat.objects.filter(user=user).delete()
        characters = self.get_user_characters(user)
        # for year in range(2014, datetime.utcnow().year + 1):
        #     for month in range(1, 13):
        #         pass
        for character in characters:
            stats = self.get_character_stats(characterId=character.character_id)
            if stats:
                for key, stat in stats.iteritems():
                    kbstat, found = KbStat.objects.get_or_create(user=user, year=stat['year'], month=stat['month'])
                    try:
                        kbstat.shipsDestroyed += stat['shipsDestroyed']
                    except:
                        pass
                    try:
                        kbstat.shipsLost += stat['shipsLost']
                    except:
                        pass
                    try:
                        kbstat.iskDestroyed += stat['iskDestroyed']
                    except:
                        pass
                    try:
                        kbstat.iskLost += stat['iskLost']
                    except:
                        pass
                    kbstat.save()
                years = [x for x in range(2014, datetime.utcnow().year+1)]
                months = [x for x in range(01, 13)]
                for year in years:
                    for month in months:
                        kbstat, created = KbStat.objects.get_or_create(user=user, year=str(year), month=str(month))
                        if created:
                            kbstat.shipsDestroyed = 0
                            kbstat.shipsLost = 0
                            kbstat.iskDestroyed = 0
                            kbstat.iskLost = 0
                            kbstat.save()
            # time.sleep(.5)
    def get_all_stats(self):
        KbStat.objects.all().delete()
        for user in User.objects.all():
            self.get_user_stats(user=user)

class KbThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        print "Starting " + self.name
        kb = KbStat()
        kb.get_all_stats()
        print "Exiting " + self.name
