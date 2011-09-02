from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout, password_reset, password_reset_confirm,\
    password_reset_done, password_change, password_change_done, password_reset_complete
from django.views.generic.simple import redirect_to, direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'zyxt.views.home', name='home'),
    # url(r'^zyxt/', include('zyxt.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', direct_to_template, {'template': 'index.html'}),
    url(r'^rules/$', direct_to_template, {'template': 'rules.html'}),
    url(r'^accounts/registration/$', 'zyxt.app.views.registration'),
    url(r'^accounts/login/$', login),
    url(r'^accounts/logout/$', logout),
    url(r'^accounts/password/$', redirect_to, {'url': '/'}),
    url(r'^accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm),
    url(r'^accounts/password/reset/complete/$', password_reset_complete),
    url(r'^accounts/password/reset/$', password_reset),
    url(r'^accounts/password/reset/done/$', password_reset_done),
    url(r'^accounts/password/change/$', password_change),
    url(r'^accounts/password/change/done/$', password_change_done),
    url(r'^mu-ba257cdb-f20580a8-81b8c94e-2915deab/$', direct_to_template, {'template': 'blitz.html', 'extra_context': {'data': '42'}}),
)

urlpatterns += patterns('zyxt.app.views',
    url(r'^quiz/$', 'quiz_index'),
    url(r'^quiz/(?P<id>\d{1,2})/$', 'quiz_description'),
    url(r'^quiz/(?P<id>\d{1,2})/(?P<level>\d{1,2})/$', 'quiz'),
    url(r'^quiz/(?P<id>\d{1,2})/(?P<level>\d{1,2})/(?P<restart>\d{0,1})/$', 'quiz'),
    url(r'^hof/$', 'halls_of_fame'),
    url(r'^hof/(?P<id>\d{1,2})/$', 'halls_of_fame'),
)
