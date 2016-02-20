from django.conf.urls import patterns, include, url

#from django.views.generic import list_detail

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from grbcatalog.grb.models import grb

grb_info = {
            'queryset': grb.objects.all(),
            'template_name': 'grb_list_page.html',
            }

urlpatterns = patterns('',
    url(r'^$', 'grbcatalog.grb.views.grb_main_page', name='grb_main_page'),
    url(r'^histo$', 'grbcatalog.grb.views.histo', name='histo'),
    url(r'^histo_page$', 'grbcatalog.grb.views.histo_page', name='histo_page'),
    url(r'^corr_plot$', 'grbcatalog.grb.views.corr_plot', name='corr_plot'),
    url(r'^corr_page$', 'grbcatalog.grb.views.corr_page', name='corr_page'),
    url(r'^plot_3d$', 'grbcatalog.grb.views.plot_3d', name='plot_3d'),
    url(r'^plot_3d_page$', 'grbcatalog.grb.views.plot_3d_page', name='plot_3d_page'),
    url(r'^help_page$', 'grbcatalog.grb.views.help_page', name='help_page'),
    url(r'^grb_page$', 'grbcatalog.grb.views.grb_page', name='grb_page'),
    # Examples:
    # url(r'^$', 'grbcatalog.views.home', name='home'),
    # url(r'^grbcatalog/', include('grbcatalog.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
