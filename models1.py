# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Reference105(models.Model):
    field_idrref = models.TextField(db_column='_IDRRef', primary_key=True)  # Field name made lowercase. Field renamed because it started with '_'. This field type is a guess.
    field_version = models.TextField(db_column='_Version')  # Field name made lowercase. Field renamed because it started with '_'. This field type is a guess.
    field_marked = models.TextField(db_column='_Marked')  # Field name made lowercase. Field renamed because it started with '_'. This field type is a guess.
    field_ismetadata = models.TextField(db_column='_IsMetadata')  # Field name made lowercase. Field renamed because it started with '_'. This field type is a guess.
    field_ownerid_type = models.TextField(db_column='_OwnerID_TYPE')  # Field name made lowercase. Field renamed because it started with '_'. This field type is a guess.
    field_ownerid_rtref = models.TextField(db_column='_OwnerID_RTRef')  # Field name made lowercase. Field renamed because it started with '_'. This field type is a guess.
    field_ownerid_rrref = models.TextField(db_column='_OwnerID_RRRef')  # Field name made lowercase. Field renamed because it started with '_'. This field type is a guess.
    field_code = models.CharField(db_column='_Code', max_length=9, db_collation='Cyrillic_General_CI_AS')  # Field name made lowercase. Field renamed because it started with '_'.
    field_description = models.CharField(db_column='_Description', max_length=50, db_collation='Cyrillic_General_CI_AS')  # Field name made lowercase. Field renamed because it started with '_'.
    field_fld2487rref = models.TextField(db_column='_Fld2487RRef')  # Field name made lowercase. Field renamed because it started with '_'. This field type is a guess.
    field_fld2488 = models.DecimalField(db_column='_Fld2488', max_digits=15, decimal_places=3)  # Field name made lowercase. Field renamed because it started with '_'.
    field_fld2489 = models.DecimalField(db_column='_Fld2489', max_digits=15, decimal_places=3)  # Field name made lowercase. Field renamed because it started with '_'.
    field_fld2490 = models.DecimalField(db_column='_Fld2490', max_digits=10, decimal_places=3)  # Field name made lowercase. Field renamed because it started with '_'.
    field_fld2491 = models.DecimalField(db_column='_Fld2491', max_digits=10, decimal_places=0)  # Field name made lowercase. Field renamed because it started with '_'.
    field_fld2492 = models.TextField(db_column='_Fld2492')  # Field name made lowercase. Field renamed because it started with '_'. This field type is a guess.

    class Meta:
        managed = False
        db_table = '_Reference105'
        unique_together = (('field_ownerid_type', 'field_ownerid_rtref', 'field_ownerid_rrref', 'field_code', 'field_idrref'), ('field_ownerid_type', 'field_ownerid_rtref', 'field_ownerid_rrref', 'field_description', 'field_idrref'), ('field_code', 'field_idrref'), ('field_description', 'field_idrref'),)
