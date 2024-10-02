import uuid
from django.db import models, transaction

class BasicUnitBook(models.Model):
    db_id = models.BinaryField(db_column='_IDRRef', unique=True)
    name = models.CharField(db_column='_Description', max_length=25, db_collation='Cyrillic_General_CI_AS')

    class Meta:
        managed = False
        db_table = '_Reference123'

    def __str__(self):
        return self.name

class ProductionTypeBook(models.Model):
    # id = models.IntegerField(db_column='id', primary_key=True, editable=False)
    reproduction = models.BinaryField (db_column='Code', unique=True)
    name = models.CharField(db_column='Name', max_length=100)

    class Meta:
        managed = False
        db_table = 'my_type_of_production_N'

    def __str__(self):
        return self.name

class NomencBook(models.Model):
    # id = models.IntegerField(db_column='id', primary_key=True, editable=False)
    db_id = models.BinaryField(db_column='_IDRRef', editable=False)

    name = models.CharField(db_column='_Description', max_length=100, db_collation='Cyrillic_General_CI_AS')
    group = models.BinaryField(db_column='_ParentIDRRef', max_length=16, default=b'\x00' * 16, editable=False) # TODO Тут необходимо реализовать возможность выбора группы номенклатуры из списка! Надо будет убрать "editable=False"
    view = models.BinaryField(db_column='_Fld3204RRef', max_length=16, default=b'\xBA\x80\x0C\xC4\x7A\x22\x9A\x23\x11\xE6\xC8\x40\x91\x63\x13\x34', editable=False)  # TODO Тут необходимо реализовать возможность выбора вида номенклатуры из списка! Надо будет убрать "editable=False"

    type_of_reproduction = models.BinaryField(db_column='_Fld3203RRef', max_length=16, blank=True, null=True, editable=True)    # Поле содержащее "Вид воспроизводства"
    basic_unit = models.BinaryField(db_column='_Fld3207RRef', blank=True, null=True, editable=True)  # Поле содержащее "Базовая единица измерения"
    basic_unit_1 = models.BinaryField(db_column='_Fld3206RRef', blank=True, null=True, editable=True)  # Поле содержащее "Единица хранения остатков": = "Базовая единица измерения"
    basic_unit_2 = models.BinaryField(db_column='_Fld3205RRef', blank=True, null=True, editable=True)  # Поле содержащее "Единица для отчетов": = "Базовая единица измерения"

    field_code = models.CharField(db_column='_Code', max_length=11, db_collation='Cyrillic_General_CI_AS', editable=False)  # Поле содержащее "Код"

    # Поля, которые должны иметь значения для сохранения записи:
    field_marked = models.BinaryField(db_column='_Marked', default=b'\x00', editable=False)
    field_ismetadata = models.BinaryField(db_column='_IsMetadata', default=b'\x00', editable=False)
    field_folder = models.BinaryField(db_column='_Folder', default=b'\x01', editable=False) # TODO тут будет реализовать выбор - создаем "папку/она же группа" или нет
    field_Fld3227RRef = models.BinaryField(db_column='_Fld3227RRef', max_length=16, default=b'\x00' * 16, editable=False) # TODO что это такое пока непонятно! Если получиться разобраться - хорошо, по всем записям одинаковая запись "0x00000000000000000000000000000000"

    class Meta:
        managed = False
        db_table = '_Reference175'

    @property
    def type_of_reproduction_display(self):
        # Получаем объект из ProductionTypeBook, используя значение в type_of_reproduction
        try:
            prod = ProductionTypeBook.objects.get(reproduction=self.type_of_reproduction)
            return prod.name
        except ProductionTypeBook.DoesNotExist:
            return None

    @property
    def basic_unit_display(self):
        # Получаем объект из BasicUnitBook, используя значение в basic_unit
        try:
            prod = BasicUnitBook.objects.get(db_id=self.basic_unit)
            return prod.name
        except BasicUnitBook.DoesNotExist:
            return None

    def write(self, *args, **kwargs):

        if not self.db_id:
            self.db_id = uuid.UUID(bytes=uuid.uuid4().bytes).bytes

        if not self.field_code:
            # Получаем текущее максимальное значение _Code
            with transaction.atomic():
                last_record = NomencBook.objects.order_by('-field_code').first()
                if last_record and last_record.field_code.strip().isdigit():
                    new_code = int(last_record.field_code.strip()) + 1
                else:
                    new_code = 1  # Начинаем с 1, если таблица пуста или значение не числовое

                # Форматируем новый код как строку длиной 11 символов
                self.field_code = str(new_code).zfill(11)

        super().save(*args, **kwargs)

class NomencUnitBook(models.Model):
    db_id = models.BinaryField(db_column='_IDRRef', editable=False) # TODO тут надо генерить значение uuid и потом его передавать в basic_unit_1 и basic_unit_2 NomencBook
    field_marked = models.BinaryField(db_column='_Marked', default=b'\x00', editable=False)
    field_ismetadata = models.BinaryField(db_column='_IsMetadata', default=b'\x00', editable=False)
    field_ownerid_type = models.BinaryField( db_column='_OwnerID_TYPE', default=b'\x08', editable=False)
    field_ownerid_rtref = models.BinaryField( db_column='_OwnerID_RTRef', default=b'\x00\x00\x00\xAF', editable=False)
    field_fld2492 = models.BinaryField(db_column='_Fld2492', default=b'\x00', editable=False)

    field_ownerid_rrref = models.BinaryField( db_column='_OwnerID_RRRef', editable=False) # TODO сюда надо подставлять значения из db_id NomencBook
    field_fld2487rref = models.BinaryField(db_column='_Fld2487RRef', editable=False) # TODO сюда надо подставлять значения из basic_unit NomencBook
    field_description = models.CharField(db_column='_Description', max_length=50, db_collation='Cyrillic_General_CI_AS')  # TODO сюда надо подставлять значения из name BasicUnitBook

    field_code = models.CharField(db_column='_Code', max_length=9, db_collation='Cyrillic_General_CI_AS')

    field_fld2488 = models.DecimalField(db_column='_Fld2488', max_digits=15, decimal_places=3, default=0.000)
    field_fld2489 = models.DecimalField(db_column='_Fld2489', max_digits=15, decimal_places=3, default=0.000)
    field_fld2490 = models.DecimalField(db_column='_Fld2490', max_digits=10, decimal_places=3, default=1.000)
    field_fld2491 = models.DecimalField(db_column='_Fld2491', max_digits=10, decimal_places=0, default=0)


    class Meta:
        managed = False
        db_table = '_Reference105'
        unique_together = (
        ('field_ownerid_type', 'field_ownerid_rtref', 'field_ownerid_rrref', 'field_code', 'field_idrref'),
        ('field_ownerid_type', 'field_ownerid_rtref', 'field_ownerid_rrref', 'field_description', 'field_idrref'),
        ('field_code', 'field_idrref'), ('field_description', 'field_idrref'),)

    def write(self, *args, **kwargs):

        if not self.db_id:
            self.db_id = uuid.UUID(bytes=uuid.uuid4().bytes).bytes

        if not self.field_code:
            # Получаем текущее максимальное значение _Code
            with transaction.atomic():
                last_record = NomencUnitBook.objects.order_by('-field_code').first()
                if last_record and last_record.field_code.strip().isdigit():
                    new_code = int(last_record.field_code.strip()) + 1
                else:
                    new_code = 1  # Начинаем с 1, если таблица пуста или значение не числовое

                # Форматируем новый код как строку длиной 11 символов
                self.field_code = str(new_code).zfill(11)

        super().save(*args, **kwargs)