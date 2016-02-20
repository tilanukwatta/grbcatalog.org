"""
Author : Tilan Ukwatta (tilan.ukwatta@gmail.com)
"""
from django.db import models
from django.contrib.auth.models import User

# ADC Custom References "%T"  "%A"  "%D" "%J" "%V"  "%p"
class reference(models.Model):
    reference_id = models.AutoField(primary_key=True)
    title = models.TextField(null=True, blank=True, help_text='Enter the reference title')
    authors = models.TextField(null=True, blank=True, help_text='Enter the authors')
    date = models.DateField(help_text='The date the reference published')
    journal = models.CharField(max_length=100, null=True, blank=True, help_text='Enter the journal name')
    volume = models.CharField(max_length=100, null=True, blank=True, help_text='Enter the journal volume')
    pages = models.CharField(max_length=100, null=True, blank=True, help_text='Enter the journal pages')
    catalog = models.CharField(max_length=100, null=True, blank=True, help_text='Enter the catalog name')
    gcn_circular = models.CharField(max_length=100, null=True, blank=True, help_text='Enter the GCN circular number')
    gcn_report = models.CharField(max_length=100, null=True, blank=True, help_text='Enter the GCN report number')
    url = models.URLField(null=True, blank=True, help_text='Enter the GCN report number')
    entry_person = models.ForeignKey(User, related_name='reference_entered_by')
    comments = models.TextField(null=True, blank=True, help_text='Enter notes')

    def __unicode__(self):
        return '{0}:{1}:{2}'.format(str(self.catalog), str(self.journal), str(self.gcn_circular))

    class Meta:
        #ordering = ['group', 'category', 'sub_category']
        #unique_together = ( 'group', 'category', 'sub_category')
        verbose_name_plural = "References"

class measurement_type(models.Model):
    measurement_type_id = models.AutoField(primary_key=True)
    measurement_type_name = models.CharField(db_index=True, max_length=100, unique=True, help_text='Enter the name')
    data_type = models.CharField(db_index=True, max_length=10)
    units = models.CharField(max_length=100, null=True, blank=True, help_text='Enter the units')
    units_latex = models.CharField(max_length=100, null=True, blank=True, help_text='Enter units in latex format')
    reference = models.ForeignKey(reference, related_name='measurement_type_reference')
    entry_person = models.ForeignKey(User, related_name='measurement_type_entered_by')
    comments = models.TextField(null=True, blank=True, help_text='Enter notes')

    def __unicode__(self):
        return '{0}'.format(str(self.measurement_type_name))

    class Meta:
        #ordering = ['group', 'category', 'sub_category']
        #unique_together = ( 'group', 'category', 'sub_category')
        verbose_name_plural = "Measurement Types"

class observatory(models.Model):
    observatory_id = models.AutoField(primary_key=True)
    observatory_name = models.CharField(db_index=True, max_length=100, null=True, blank=True, help_text='Enter the name of the observatory')
    instrument = models.CharField(db_index=True, max_length=100, null=True, blank=True, help_text='Enter the name of the instrument')
    start_date = models.DateField(help_text='The date the observatory/instrument activated')
    end_date = models.DateField(null=True, blank=True, help_text='The date the observatory/instrument deactivated')
    reference = models.ForeignKey(reference, related_name='observatory_reference')
    entry_person = models.ForeignKey(User, related_name='observatory_entered_by')
    comments = models.TextField(null=True, blank=True, help_text='Enter notes')

    def __unicode__(self):
        return '{0}:{1}'.format(str(self.observatory_name), str(self.instrument))

    class Meta:
        verbose_name_plural = "Observatories"

class grb_type(models.Model):
    grb_type_id = models.AutoField(primary_key=True)
    grb_type_name = models.CharField(db_index=True, max_length=100, unique=True, help_text='Enter the name of the observatory')
    reference = models.ForeignKey(reference, related_name='grb_type_reference')
    entry_person = models.ForeignKey(User, related_name='grb_type_entered_by')
    comments = models.TextField(null=True, blank=True, help_text='Enter notes')

    def __unicode__(self):
        return '{0}'.format(str(self.grb_type_name))

    class Meta:
        verbose_name_plural = "GRB Types"

class grb(models.Model):
    grb_id = models.AutoField(primary_key=True)
    grb_name = models.CharField(db_index=True, max_length=20, unique=True)
    #date = models.DateTimeField(db_index=True, help_text='Enter the date and time of the burst')
    #best_ra = models.FloatField(db_index=True, help_text='Enter best known RA')
    #best_dec = models.FloatField(db_index=True, help_text='Enter best known DEC')
    #best_pos_err = models.FloatField(db_index=True, help_text='Enter best position error')
    entry_person = models.ForeignKey(User, related_name='grb_entered_by')
    comments = models.TextField(null=True, blank=True, help_text='Enter notes')

    def __unicode__(self):
        return '{0}'.format(str(self.grb_name))
    
    class Meta:
        ordering = ['-grb_name']
        verbose_name_plural = "GRBs"

class measurement(models.Model):
    measurement_id = models.AutoField(primary_key=True)
    grb_name = models.ForeignKey(grb, related_name='grb_measurement')
    measurement_type = models.ForeignKey(measurement_type, related_name='type')
    value = models.FloatField(db_index=True, help_text='Enter value')
    value_error_positive = models.FloatField(null=True, blank=True, help_text='Enter positive error')
    value_error_negative = models.FloatField(null=True, blank=True, help_text='Enter negative error')
    text = models.TextField(null=True, blank=True, help_text='Enter measurement notes')
    date = models.DateTimeField(null=True, blank=True, help_text='Enter date measurement')
    reference = models.ForeignKey(reference, related_name='measurement_reference')
    entry_person = models.ForeignKey(User, related_name='measurement_entered_by')

    def __unicode__(self):
        return '{0}'.format(str(self.grb_name))

    class Meta:
        verbose_name_plural = "Measurements"

class grb_type_list(models.Model):
    grb_type_list_id = models.AutoField(primary_key=True)
    grb_name = models.ForeignKey(grb)
    grb_type = models.ForeignKey(grb_type, related_name='type')
    reference = models.ForeignKey(reference, related_name='grb_type_list_reference')
    entry_person = models.ForeignKey(User, related_name='grb_type_list_entered_by')
    comments = models.TextField(null=True, blank=True, help_text='Enter notes')

    def __unicode__(self):
        return '{0}:{1}'.format(str(self.grb_name), str(self.grb_type))

    class Meta:
        verbose_name_plural = "GRB Type List"

class grb_observatory_list(models.Model):
    grb_observatory_list_id = models.AutoField(primary_key=True)
    grb_name = models.ForeignKey(grb)
    observatory = models.ForeignKey(observatory)
    trigger_number = models.IntegerField(db_index=True, null=True, blank=True, help_text='Enter trigger number (unique for a given observatory)')
    reference = models.ForeignKey(reference, related_name='grb_observatory_list_reference')
    entry_person = models.ForeignKey(User, related_name='grb_observatory_list_entered_by')
    comments = models.TextField(null=True, blank=True, help_text='Enter notes')

    def __unicode__(self):
        return '{0}:{1}'.format(str(self.grb_name), str(self.observatory))

    class Meta:
        verbose_name_plural = "GRB Observatory List"

class help(models.Model):
    help_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=250, unique=True, help_text='Enter help title')
    description = models.TextField(null=True, blank=True, help_text='Enter help description')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "GRB Catalog Help"
