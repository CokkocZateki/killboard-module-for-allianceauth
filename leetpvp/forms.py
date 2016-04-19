__author__ = 'tyler274'
from django import forms
from django.contrib.auth.models import Group

from eveonline.models import EveCorporationInfo
from datetime import datetime
from models import KbStat


class KbReportForm(forms.Form):
    year_choices = [
        (x, x) for x in range(2014, datetime.utcnow().year+1)
        ]
    corp_choices = [
        (x, x) for x in Group.objects.filter(name__startswith='Corp_')
    ]
    year = forms.ChoiceField(initial=datetime.utcnow().year, choices=year_choices, required=False)
    month = forms.ChoiceField(initial=datetime.utcnow().month - 1, choices=[(x, x) for x in range(1, 13)], required=False)
    corp = forms.ChoiceField(choices=corp_choices)

    def get_stat_data(self):
        corp_name = self.cleaned_data['corp'].split('Corp_', 1)[1].replace('_', ' ')
        stats = KbStat.objects.filter(year=self.cleaned_data['year'],
                                      month=self.cleaned_data['month'],
                                      user__evecharacter__corporation_name=corp_name)
        return stats


