"""
Author : Tilan Ukwatta (tilan.ukwatta@gmail.com) for the HAWC Collaboration
"""
from django.contrib import admin
from grbcatalog.grb.models import grb, reference, measurement_type, observatory, grb_type, measurement, grb_type_list, grb_observatory_list, help

class grbAdmin(admin.ModelAdmin):
    list_display = ('grb_id',
                    'grb_name',
                    'entry_person',
                    'comments')
    search_fields = ('grb_name', 'entry_person', 'comments')
    #list_filter = ('mission','redshift')

admin.site.register(grb, grbAdmin)

class referenceAdmin(admin.ModelAdmin):
    list_display = ('reference_id',
                    'title',
                    'authors',
                    'date',
                    'journal',
                    'volume',
                    'pages',
                    'catalog',
                    'gcn_circular',
                    'gcn_report',
                    'url',
                    'entry_person',
                    'comments')
    search_fields = ('title',
                     'authors',
                     'date',
                     'journal',
                     'volume',
                     'pages',
                     'catalog',
                     'gcn_circular',
                     'gcn_report',
                     'url',
                     'entry_person',
                     'comments')
    #list_filter = ('mission','redshift')

admin.site.register(reference, referenceAdmin)

class measurement_typeAdmin(admin.ModelAdmin):
    list_display = ('measurement_type_id',
                    'measurement_type_name',
                    'data_type',
                    'units',
                    'units_latex',
                    'reference',
                    'entry_person',
                    'comments')
    search_fields = ('measurement_type_name',
                     'units',
                     'units_latex',
                     'reference',
                     'entry_person',
                     'comments')
    #list_filter = ('mission','redshift')

admin.site.register(measurement_type, measurement_typeAdmin)

class observatoryAdmin(admin.ModelAdmin):
    list_display = ('observatory_id',
                    'observatory_name',
                    'instrument',
                    'start_date',
                    'end_date',
                    'reference',
                    'entry_person',
                    'comments')
    search_fields = ('observatory_name',
                     'instrument',
                     'start_date',
                     'end_date',
                     'reference',
                     'entry_person',
                     'comments')
    #list_filter = ('mission','redshift')

admin.site.register(observatory, observatoryAdmin)

class grb_typeAdmin(admin.ModelAdmin):
    list_display = ('grb_type_id',
                    'grb_type_name',
                    'reference',
                    'entry_person',
                    'comments')
    search_fields = ('grb_type_name',
                     'reference',
                     'entry_person',
                     'comments')
    #list_filter = ('mission','redshift')

admin.site.register(grb_type, grb_typeAdmin)

class measurementAdmin(admin.ModelAdmin):
    list_display = ('measurement_id',
                    'grb_name',
                    'measurement_type',
                    'value',
                    'text',
                    'value_error_positive',
                    'value_error_negative',
                    'reference',
                    'entry_person')
    search_fields = ('grb_name__grb_name',
                     'measurement_type__measurement_type_name',
                     'value',
                     'text')
    #list_filter = ('mission','redshift')

admin.site.register(measurement, measurementAdmin)

class grb_type_listAdmin(admin.ModelAdmin):
    list_display = ('grb_type_list_id',
                    'grb_name',
                    'grb_type',
                    'reference',
                    'entry_person',
                    'comments')
    search_fields = ('grb_name',
                     'grb_type',
                     'reference',
                     'entry_person',
                     'comments')
    #list_filter = ('mission','redshift')

admin.site.register(grb_type_list, grb_type_listAdmin)

class grb_observatory_listAdmin(admin.ModelAdmin):
    list_display = ('grb_observatory_list_id',
                    'grb_name',
                    'observatory',
                    'trigger_number',
                    'reference',
                    'entry_person',
                    'comments')
    search_fields = ('grb_name',
                     'observatory',
                     'trigger_number',
                     'reference',
                     'entry_person',
                     'comments')
    #list_filter = ('mission','redshift')

admin.site.register(grb_observatory_list, grb_observatory_listAdmin)

class helpAdmin(admin.ModelAdmin):
    list_display = ('help_id',
                    'name',
                    'title',
                    'description')
    search_fields = ('name',
                    'title',
                    'description')

admin.site.register(help, helpAdmin)

