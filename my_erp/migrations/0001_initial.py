# Generated by Django 4.2 on 2024-12-02 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BasicUnitBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_id', models.BinaryField(db_column='_IDRRef', max_length='max', unique=True)),
                ('name', models.CharField(db_collation='Cyrillic_General_CI_AS', db_column='_Description', max_length=25)),
            ],
            options={
                'verbose_name': 'Базовые единицы измерения',
                'verbose_name_plural': 'Базовые единицы измерения',
                'db_table': '_Reference123',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='NomencBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_id', models.BinaryField(db_column='_IDRRef', max_length='max')),
                ('field_code', models.CharField(db_collation='Cyrillic_General_CI_AS', db_column='_Code', editable=False, max_length=11)),
                ('field_folder', models.BinaryField(db_column='_Folder', default=b'\x01', max_length='max')),
                ('field_marked', models.BinaryField(db_column='_Marked', default=b'\x00', max_length='max')),
                ('name', models.CharField(db_collation='Cyrillic_General_CI_AS', db_column='_Description', max_length=100, verbose_name='Наименование')),
                ('group', models.BinaryField(db_column='_ParentIDRRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length=16)),
                ('view', models.BinaryField(db_column='_Fld3204RRef', default=b'\xba\x80\x0c\xc4z"\x9a#\x11\xe6\xc8@\x91c\x134', max_length=16)),
                ('articles', models.TextField(blank=True, db_collation='Cyrillic_General_CI_AS', db_column='_Fld3194', default='', max_length=25, null=True, verbose_name='Артикур')),
                ('comment', models.TextField(blank=True, db_collation='Cyrillic_General_CI_AS', db_column='_Fld3211', null=True, verbose_name='Комментарий')),
                ('full_name', models.TextField(blank=True, db_collation='Cyrillic_General_CI_AS', db_column='_Fld3195', null=True, verbose_name='Полное наименование')),
                ('description', models.TextField(blank=True, db_collation='Cyrillic_General_CI_AS', db_column='_Fld3231', default='', editable=False, null=True, verbose_name='Описание')),
                ('type_of_reproduction', models.BinaryField(blank=True, db_column='_Fld3203RRef', editable=True, max_length=16, null=True)),
                ('basic_unit', models.BinaryField(blank=True, db_column='_Fld3207RRef', editable=True, max_length='max', null=True)),
                ('basic_unit_1', models.BinaryField(db_column='_Fld3206RRef', max_length='max')),
                ('basic_unit_2', models.BinaryField(db_column='_Fld3205RRef', max_length='max')),
                ('field_ismetadata', models.BinaryField(db_column='_IsMetadata', default=b'\x00', max_length='max')),
                ('field_fld3227rref', models.BinaryField(blank=True, db_column='_Fld3227RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld3198', models.BinaryField(blank=True, db_column='_Fld3198', default=b'\x01', max_length='max', null=True)),
                ('field_fld3200', models.BinaryField(blank=True, db_column='_Fld3200', default=b'\x00', max_length='max', null=True)),
                ('field_fld3213', models.BinaryField(blank=True, db_column='_Fld3213', default=b'\x00', max_length='max', null=True)),
                ('field_fld37899', models.BinaryField(blank=True, db_column='_Fld37899', default=b'\x00', max_length='max', null=True)),
                ('field_fld3215rref', models.BinaryField(blank=True, db_column='_Fld3215RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld3222rref', models.BinaryField(blank=True, db_column='_Fld3222RRef', default=b'\xba\x82\x0c\xc4z"\x9a#\x11\xe6\xd6\xfc,|\xa8\xfd', max_length='max', null=True)),
                ('field_fld3225rref', models.BinaryField(blank=True, db_column='_Fld3225RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld3228rref', models.BinaryField(blank=True, db_column='_Fld3228RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld3210rref', models.BinaryField(blank=True, db_column='_Fld3210RRef', default=b'\xbe\xd8\xa5\x0fg2\x88\xeb@\x0c\xbb\xd4V+\x97\x9b', max_length='max', null=True)),
                ('field_fld3212rref', models.BinaryField(blank=True, db_column='_Fld3212RRef', default=b'\xba\x82\x0c\xc4z"\x9a#\x11\xe6\xd6Y\xdf\xe5Bd', max_length='max', null=True)),
                ('field_fld3217rref', models.BinaryField(blank=True, db_column='_Fld3217RRef', default=b'\xba\x82\x0c\xc4z"\x9a#\x11\xe6\xd6Y\xdf\xe5Bd', max_length='max', null=True)),
                ('field_fld3214rref', models.BinaryField(blank=True, db_column='_Fld3214RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld3218rref', models.BinaryField(blank=True, db_column='_Fld3218RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld3232rref', models.BinaryField(blank=True, db_column='_Fld3232RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld3233rref', models.BinaryField(blank=True, db_column='_Fld3233RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld3240rref', models.BinaryField(blank=True, db_column='_Fld3240RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld32966', models.CharField(blank=True, db_collation='Cyrillic_General_CI_AS', db_column='_Fld32966', default='', editable=False, max_length=13, null=True)),
                ('field_fld3197', models.DecimalField(db_column='_Fld3197', decimal_places=0, default=0, editable=False, max_digits=10, null=True)),
                ('field_fld3237', models.DecimalField(db_column='_Fld3237', decimal_places=6, default=0.0, editable=False, max_digits=18)),
                ('field_fld3239', models.DecimalField(db_column='_Fld3239', decimal_places=3, default=0.0, editable=False, max_digits=5)),
                ('field_fld34164', models.DecimalField(db_column='_Fld34164', decimal_places=11, default=0.0, editable=False, max_digits=23)),
                ('field_fld3196', models.BinaryField(blank=True, db_column='_Fld3196', default=b'\x00', max_length='max', null=True)),
                ('field_fld3199', models.BinaryField(blank=True, db_column='_Fld3199', default=b'\x00', max_length='max', null=True)),
                ('field_fld3201', models.BinaryField(blank=True, db_column='_Fld3201', default=b'\x00', max_length='max', null=True)),
                ('field_fld3202', models.BinaryField(blank=True, db_column='_Fld3202', default=b'\x00', max_length='max', null=True)),
                ('field_fld3208', models.BinaryField(blank=True, db_column='_Fld3208', default=b'\x00', max_length='max', null=True)),
                ('field_fld3220', models.BinaryField(blank=True, db_column='_Fld3220', default=b'\x00', max_length='max', null=True)),
                ('field_fld3221', models.BinaryField(blank=True, db_column='_Fld3221', default=b'\x00', max_length='max', null=True)),
                ('field_fld3223', models.BinaryField(blank=True, db_column='_Fld3223', default=b'\x00', max_length='max', null=True)),
                ('field_fld3224', models.BinaryField(blank=True, db_column='_Fld3224', default=b'\x00', max_length='max', null=True)),
                ('field_fld3234', models.BinaryField(blank=True, db_column='_Fld3234', default=b'\x00', max_length='max', null=True)),
                ('field_fld3235', models.BinaryField(blank=True, db_column='_Fld3235', default=b'\x00', max_length='max', null=True)),
                ('field_fld3236', models.BinaryField(blank=True, db_column='_Fld3236', default=b'\x00', max_length='max', null=True)),
                ('field_fld31409', models.BinaryField(blank=True, db_column='_Fld31409', default=b'\x00', max_length='max', null=True)),
                ('field_fld32059', models.BinaryField(blank=True, db_column='_Fld32059', default=b'\x00', max_length='max', null=True)),
                ('field_fld32853', models.BinaryField(blank=True, db_column='_Fld32853', default=b'\x00', max_length='max', null=True)),
                ('field_fld36355', models.BinaryField(blank=True, db_column='_Fld36355', default=b'\x00', max_length='max', null=True)),
                ('field_fld3209rref', models.BinaryField(blank=True, db_column='_Fld3209RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld3216rref', models.BinaryField(blank=True, db_column='_Fld3216RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld3219rref', models.BinaryField(blank=True, db_column='_Fld3219RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld3226rref', models.BinaryField(blank=True, db_column='_Fld3226RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld3229rref', models.BinaryField(blank=True, db_column='_Fld3229RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld3230rref', models.BinaryField(blank=True, db_column='_Fld3230RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld3238rref', models.BinaryField(blank=True, db_column='_Fld3238RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld32060rref', models.BinaryField(blank=True, db_column='_Fld32060RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld33045rref', models.BinaryField(blank=True, db_column='_Fld33045RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld34165rref', models.BinaryField(blank=True, db_column='_Fld34165RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
                ('field_fld37835rref', models.BinaryField(blank=True, db_column='_Fld37835RRef', default=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', max_length='max', null=True)),
            ],
            options={
                'verbose_name': 'Номенклатура',
                'verbose_name_plural': 'Номенклатура',
                'db_table': '_Reference175',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='NomencUnitBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_id', models.BinaryField(db_column='_IDRRef', max_length='max')),
                ('field_marked', models.BinaryField(db_column='_Marked', default=b'\x00', max_length='max')),
                ('field_ismetadata', models.BinaryField(db_column='_IsMetadata', default=b'\x00', max_length='max')),
                ('field_ownerid_type', models.BinaryField(db_column='_OwnerID_TYPE', default=b'\x08', max_length='max')),
                ('field_ownerid_rtref', models.BinaryField(db_column='_OwnerID_RTRef', default=b'\x00\x00\x00\xaf', max_length='max')),
                ('field_fld2492', models.BinaryField(db_column='_Fld2492', default=b'\x00', max_length='max')),
                ('field_ownerid_rrref', models.BinaryField(db_column='_OwnerID_RRRef', max_length='max')),
                ('field_fld2487rref', models.BinaryField(db_column='_Fld2487RRef', max_length='max')),
                ('field_description', models.CharField(db_collation='Cyrillic_General_CI_AS', db_column='_Description', max_length=50)),
                ('field_code', models.CharField(db_collation='Cyrillic_General_CI_AS', db_column='_Code', editable=False, max_length=9)),
                ('field_fld2488', models.DecimalField(db_column='_Fld2488', decimal_places=3, default=0.0, editable=False, max_digits=15)),
                ('field_fld2489', models.DecimalField(db_column='_Fld2489', decimal_places=3, default=0.0, editable=False, max_digits=15)),
                ('field_fld2490', models.DecimalField(db_column='_Fld2490', decimal_places=3, default=1.0, editable=False, max_digits=10)),
                ('field_fld2491', models.DecimalField(db_column='_Fld2491', decimal_places=0, default=0, editable=False, max_digits=10)),
            ],
            options={
                'db_table': '_Reference105',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ProductionTypeBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reproduction', models.BinaryField(db_column='Code', max_length='max', null=True, unique=True)),
                ('name', models.CharField(db_column='Name', max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'Вид воспроизводства',
                'verbose_name_plural': 'Вид воспроизводства',
                'db_table': 'my_type_of_production_N',
                'managed': False,
            },
        ),
    ]
