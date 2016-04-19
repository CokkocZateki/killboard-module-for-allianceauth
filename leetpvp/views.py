from django.shortcuts import render
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse

from forms import KbReportForm
from models import KbStat, KbThread
from datetime import datetime
# Create your views here.


class KbStatView(FormView):
    template_name = 'kbstat.html'
    form_class = KbReportForm
    model = KbStat
    success_url = '/kbstat'

    def get_context_data(self, **kwargs):
        context = super(KbStatView, self).get_context_data(**kwargs)
        # context['latest_articles'] = KbStat.objects.all()[:5]
        # context['ryan'] = self.get_corp_kb()
        # kb = KbStat()
        # kb.get_corp_stats()
        context['stats'] = KbStat.objects.filter(year=datetime.utcnow().year, month=datetime.utcnow().month - 1)
        return context

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # return super(KbStatView, self).form_valid(form)
        context = self.get_context_data()
        #context['stats'] = form.get_stat_data()
        corp_name = form.cleaned_data['corp'].split('Corp_', 1)[1].replace('_', ' ')
        stats = KbStat.objects.filter(year=form.cleaned_data['year'],
                                      month=form.cleaned_data['month'],
                                      user__evecharacter__corporation_name=corp_name)
        for stat in stats:
            print stat.user.username
        context['stats'] = stats
        context['form'] = form
        return render(self.request, self.template_name, context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def generate_kb_stats(request):
    kb = KbThread(1, 'kb_update', 1)
    kb.start()
    return HttpResponseRedirect(reverse('kb-stats-view'))

@login_required
def kb_stat_view(request):
    template_name = 'kbstat.html'
    context = {}
    form = None

    if request.method == 'POST':
        form = KbReportForm(request.POST)
        if form.is_valid():
            corp_name = form.cleaned_data['corp'].split('Corp_', 1)[1].replace('_', ' ')
            stats = KbStat.objects.filter(year=form.cleaned_data['year'],
                                          month=form.cleaned_data['month'],
                                          user__evecharacter__corporation_name=corp_name)
            stats = list(set(stats))
            context['stats'] = stats
    else:
        form = KbReportForm()
        context['stats'] = KbStat.objects.filter(year=datetime.utcnow().year, month=datetime.utcnow().month - 1)

    context['form'] = form

    return render(request, template_name, context)
