import uuid
from django.db import models, transaction

class BasicUnitBook(models.Model):
    db_id = models.BinaryField(db_column='_IDRRef', unique=True)
    name = models.CharField(db_column='_Description', max_length=25, db_collation='Cyrillic_General_CI_AS')

    class Meta:
        managed = False
        db_table = '_Reference123'
        verbose_name = 'Базовые единицы измерения'  # Имя модели в админке
        verbose_name_plural = 'Базовые единицы измерения'  # Множественное число в админке

    def __str__(self):
        return self.name

class ProductionTypeBook(models.Model):
    reproduction = models.BinaryField (db_column='Code', unique=True, null=True)
    name = models.CharField(db_column='Name', max_length=100, null=True)

    class Meta:
        managed = False
        db_table = 'my_type_of_production_N'
        verbose_name = 'Вид воспроизводства'  # Имя модели в админке
        verbose_name_plural = 'Вид воспроизводства'  # Множественное число в админке

    def __str__(self):
        return self.name

class NomencBook(models.Model):

    # ____ Служебные поля ____
    db_id = models.BinaryField(db_column='_IDRRef', editable=False)
    field_code = models.CharField(db_column='_Code', max_length=11, db_collation='Cyrillic_General_CI_AS', editable=False)  # Поле содержащее "Код"
    field_folder = models.BinaryField(db_column='_Folder', default=b'\x01', editable=False)  # TODO тут будет реализовать выбор - создаем "папку/она же группа" или нет
    field_marked = models.BinaryField(db_column='_Marked', default=b'\x00', editable=False)  # Маркер "На удаление"
    qnt = models.DecimalField(db_column="Qnt", max_digits=15, decimal_places=3, null=True, blank=True) # Поле с количеством, которое вычисляется в таблице Stocks внутри БД

    # ____ Поля для пользователя ____
        # Не зависят от field_folder
    name = models.CharField(db_column='_Description', max_length=100, db_collation='Cyrillic_General_CI_AS', verbose_name='Наименование') # Наименование
    group = models.BinaryField(db_column='_ParentIDRRef', max_length=16, default=b'\x00' * 16, editable=False)  # TODO Тут необходимо реализовать возможность выбора "группы номенклатуры" из списка! Надо будет убрать "editable=False"
    view = models.BinaryField(db_column='_Fld3204RRef', max_length=16, default=b'\xBA\x80\x0C\xC4\x7A\x22\x9A\x23\x11\xE6\xC8\x40\x91\x63\x13\x34', editable=False)  # TODO Тут необходимо реализовать возможность выбора "вида номенклатуры" из списка! Надо будет убрать "editable=False"
        # Поля со значением NULL, если если field_folder=0х00
    articles = models.TextField(db_column='_Fld3194', default='', max_length=25, db_collation='Cyrillic_General_CI_AS', blank=True, null=True, verbose_name='Артикур') # Артикул
    comment = models.TextField(db_column='_Fld3211', db_collation='Cyrillic_General_CI_AS', blank=True, null=True, verbose_name='Комментарий') # Поле "Комментарий"
    full_name = models.TextField(db_column='_Fld3195', db_collation='Cyrillic_General_CI_AS', blank=True, null=True, verbose_name='Полное наименование') # TODO поле "Полное наименование". Реализовать галочку, если стоит, то значение равно name
    description = models.TextField(db_column='_Fld3231', default='', editable=False, db_collation='Cyrillic_General_CI_AS', blank=True, null=True, verbose_name='Описание')  # TODO Вкладка "Описание" - поле с описание. Можно реализовать место ввода, отключив  editable=False.

    type_of_reproduction = models.BinaryField(db_column='_Fld3203RRef', max_length=16, blank=True, null=True, editable=True)  # Поле содержащее "Вид воспроизводства"

    basic_unit = models.BinaryField(db_column='_Fld3207RRef', blank=True, null=True, editable=True)  # Поле содержащее "Базовая единица измерения"
    basic_unit_1 = models.BinaryField(db_column='_Fld3206RRef', editable=False)  # Поле содержащее "Единица хранения остатков": = "Базовая единица измерения"
    basic_unit_2 = models.BinaryField(db_column='_Fld3205RRef', editable=False)  # Поле содержащее "Единица для отчетов": = "Базовая единица измерения"

    # Поля константы:
    field_ismetadata = models.BinaryField(db_column='_IsMetadata', default=b'\x00', editable=False)
    field_fld3227rref = models.BinaryField(db_column='_Fld3227RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)

    # TODO все поля ниже могут быть со значением NULL, если field_folder=0х00
    field_fld3198 = models.BinaryField(db_column='_Fld3198', default=b'\x01', editable=False, blank=True, null=True)  # TODO Это галочка "Вести оперативный учет остатков незавершенного производства" - для Вида номенклатуры=услуга всегда 0х00, т.е. надо реализовать зависимость от поля view и реализовать саму галочку
    field_fld3200 = models.BinaryField(db_column='_Fld3200', default=b'\x00', editable=False, blank=True, null=True)  # TODO Это галочка "Вести учет по: сериям" - реализовать галочку
    field_fld3213 = models.BinaryField(db_column='_Fld3213', default=b'\x00', blank=True, null=True)  # TODO если поле view=услуга, то default=b'\x01' - Тип номенклатуры
    field_fld37899 = models.BinaryField(db_column='_Fld37899', default=b'\x00', editable=False, blank=True, null=True)  # TODO Подакцизный товар, реализовать галочку (если очень захочется)
    field_fld3215rref = models.BinaryField(db_column='_Fld3215RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)  # TODO Вкладка "Дополнительно" - Основной поставщик. Почти везде ничего не указано, но возможно надо будет сделать выбор из списка
    field_fld3222rref = models.BinaryField(db_column='_Fld3222RRef', default=b'\xba\x82\x0c\xc4z"\x9a#\x11\xe6\xd6\xfc,|\xa8\xfd', editable=False, blank=True, null=True)  # TODO Статья затрат, скорее всего понадобиться сделать выбор списком
    field_fld3225rref = models.BinaryField(db_column='_Fld3225RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)  # TODO Направление выпуска, если b'\x00' * 16 = пусто в строке. Реализовать выпадающий список: на склад (0xB3701E2D2020D8E541A8D200FA70F225), на затраты (0xA4625565EF43C8BD410F8EB2FD178C6B)
    field_fld3228rref = models.BinaryField(db_column='_Fld3228RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)  # TODO Вкладка "Дополнительно" - ценовая группа. Реализовать выпадающий список.

    field_fld3210rref = models.BinaryField(db_column='_Fld3210RRef', default=b'\xbe\xd8\xa5\x0fg2\x88\xeb@\x0c\xbb\xd4V+\x97\x9b', blank=True, null=True, editable=False)  # Значение НДС - по умолчанию 20%
    field_fld3212rref = models.BinaryField(db_column='_Fld3212RRef', default=b'\xba\x82\x0c\xc4z"\x9a#\x11\xe6\xd6Y\xdf\xe5Bd', editable=False, blank=True, null=True)  # Номенклатурная группа затрат - по умолчания установленно значение "Реализация продукции"
    field_fld3217rref = models.BinaryField(db_column='_Fld3217RRef', default=b'\xba\x82\x0c\xc4z"\x9a#\x11\xe6\xd6Y\xdf\xe5Bd', editable=False, blank=True, null=True)  # Вкладка "Дополнительно" - Номенклатурная группа. По умолчания установленно значение "Реализация продукции"
    field_fld3214rref = models.BinaryField(db_column='_Fld3214RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)  # Изображение
    field_fld3218rref = models.BinaryField(db_column='_Fld3218RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)  # Страна
    field_fld3232rref = models.BinaryField(db_column='_Fld3232RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)  # Производитель во вкладке "Описание"
    field_fld3233rref = models.BinaryField(db_column='_Fld3233RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)  # Импортер
    field_fld3240rref = models.BinaryField(db_column='_Fld3240RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)  # ТН ВЭД

    field_fld32966 = models.CharField(db_column='_Fld32966', editable=False, default='', max_length=13, db_collation='Cyrillic_General_CI_AS', blank=True, null=True)

    field_fld3197 = models.DecimalField(db_column='_Fld3197', editable=False, max_digits=10, decimal_places=0, default=0, null=True)
    field_fld3237 = models.DecimalField(db_column='_Fld3237', editable=False, max_digits=18, decimal_places=6, default=0.000000)
    field_fld3239 = models.DecimalField(db_column='_Fld3239', editable=False, max_digits=5, decimal_places=3, default=0.000)
    field_fld34164 = models.DecimalField(db_column='_Fld34164', editable=False, max_digits=23, decimal_places=11, default=0.00000000000)

    field_fld3196 = models.BinaryField(db_column='_Fld3196', default=b'\x00', editable=False, blank=True, null=True)
    field_fld3199 = models.BinaryField(db_column='_Fld3199', default=b'\x00', editable=False, blank=True, null=True)
    field_fld3201 = models.BinaryField(db_column='_Fld3201', default=b'\x00', editable=False, blank=True, null=True)
    field_fld3202 = models.BinaryField(db_column='_Fld3202', default=b'\x00', editable=False, blank=True, null=True)
    field_fld3208 = models.BinaryField(db_column='_Fld3208', default=b'\x00', editable=False, blank=True, null=True)
    field_fld3220 = models.BinaryField(db_column='_Fld3220', default=b'\x00', editable=False, blank=True, null=True)
    field_fld3221 = models.BinaryField(db_column='_Fld3221', default=b'\x00', editable=False, blank=True, null=True)
    field_fld3223 = models.BinaryField(db_column='_Fld3223', default=b'\x00', editable=False, blank=True, null=True)
    field_fld3224 = models.BinaryField(db_column='_Fld3224', default=b'\x00', editable=False, blank=True, null=True)
    field_fld3234 = models.BinaryField(db_column='_Fld3234', default=b'\x00', editable=False, blank=True, null=True)
    field_fld3235 = models.BinaryField(db_column='_Fld3235', default=b'\x00', editable=False, blank=True, null=True)
    field_fld3236 = models.BinaryField(db_column='_Fld3236', default=b'\x00', editable=False, blank=True, null=True)

    field_fld31409 = models.BinaryField(db_column='_Fld31409', default=b'\x00', editable=False, blank=True, null=True)
    field_fld32059 = models.BinaryField(db_column='_Fld32059', default=b'\x00', editable=False, blank=True, null=True)
    field_fld32853 = models.BinaryField(db_column='_Fld32853', default=b'\x00', editable=False, blank=True, null=True)
    field_fld36355 = models.BinaryField(db_column='_Fld36355', default=b'\x00', editable=False, blank=True, null=True)

    field_fld3209rref = models.BinaryField(db_column='_Fld3209RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)
    field_fld3216rref = models.BinaryField(db_column='_Fld3216RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)
    field_fld3219rref = models.BinaryField(db_column='_Fld3219RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)
    field_fld3226rref = models.BinaryField(db_column='_Fld3226RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)
    field_fld3229rref = models.BinaryField(db_column='_Fld3229RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)
    field_fld3230rref = models.BinaryField(db_column='_Fld3230RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)
    field_fld3238rref = models.BinaryField(db_column='_Fld3238RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)

    field_fld32060rref = models.BinaryField(db_column='_Fld32060RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)
    field_fld33045rref = models.BinaryField(db_column='_Fld33045RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)
    field_fld34165rref = models.BinaryField(db_column='_Fld34165RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)
    field_fld37835rref = models.BinaryField(db_column='_Fld37835RRef', default=b'\x00' * 16, editable=False, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '_Reference175'
        verbose_name = 'Номенклатура'  # Имя модели в админке
        verbose_name_plural = 'Номенклатура'  # Множественное число в админке

    def get_qnt(self):
        """Возвращает 0, если qnt равно None"""
        return self.qnt if self.qnt is not None else 0

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
        # Формируем значение поля db_id
        if not self.db_id:
            self.db_id = uuid.uuid4().bytes

        # Формируем значение поля field_code
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
    db_id = models.BinaryField(db_column='_IDRRef', editable=False) # для новых записей сюда генерится значение uuid, которое потом попадает в basic_unit_1 и basic_unit_2 NomencBook
    field_marked = models.BinaryField(db_column='_Marked', default=b'\x00', editable=False) # Маркер "На удаление"
    field_ismetadata = models.BinaryField(db_column='_IsMetadata', default=b'\x00', editable=False)
    field_ownerid_type = models.BinaryField( db_column='_OwnerID_TYPE', default=b'\x08', editable=False)
    field_ownerid_rtref = models.BinaryField( db_column='_OwnerID_RTRef', default=b'\x00\x00\x00\xAF', editable=False)
    field_fld2492 = models.BinaryField(db_column='_Fld2492', default=b'\x00', editable=False)

    field_ownerid_rrref = models.BinaryField( db_column='_OwnerID_RRRef', editable=False) # тут значения из db_id NomencBook
    field_fld2487rref = models.BinaryField(db_column='_Fld2487RRef', editable=False) # тут значения из basic_unit NomencBook
    field_description = models.CharField(db_column='_Description', max_length=50, db_collation='Cyrillic_General_CI_AS')  # тут значения из name BasicUnitBook

    field_code = models.CharField(db_column='_Code', max_length=9, db_collation='Cyrillic_General_CI_AS', editable=False)

    field_fld2488 = models.DecimalField(db_column='_Fld2488', editable=False, max_digits=15, decimal_places=3, default=0.000)
    field_fld2489 = models.DecimalField(db_column='_Fld2489', editable=False, max_digits=15, decimal_places=3, default=0.000)
    field_fld2490 = models.DecimalField(db_column='_Fld2490', editable=False, max_digits=10, decimal_places=3, default=1.000)
    field_fld2491 = models.DecimalField(db_column='_Fld2491', editable=False, max_digits=10, decimal_places=0, default=0)

    class Meta:
        managed = False
        db_table = '_Reference105'

    @staticmethod
    def generate_new_code():
        # Логика генерации нового значения для field_code в NomencUnitBook
        last_record = NomencUnitBook.objects.order_by('-field_code').first()
        if last_record and last_record.field_code.strip().isdigit():
            new_code = int(last_record.field_code.strip()) + 1
        else:
            new_code = 1  # Начинаем с 1, если таблица пуста или значение не числовое

        return str(new_code).zfill(9)  # Форматируем новый код как строку длиной 9 символов
