from django.db import models



# Миксин для подтягивания наименования единицы измерения
class BasicUnitMixin:
    def get_basic_unit(self):
        from my_erp.models import BasicUnitBook
        ref_obj = getattr(self, 'nomenclature', None)
        if ref_obj and ref_obj.basic_unit:
            try:
                return BasicUnitBook.objects.get(db_id=ref_obj.basic_unit)
            except BasicUnitBook.DoesNotExist:
                return None
        return None

    @property
    def basic_unit(self):
        return self.get_basic_unit()

    @property
    def basic_unit_name(self):
        unit = self.get_basic_unit()
        return unit.name if unit else None

# Заказы покупателей
class OrdersBook(models.Model):
    db_id = models.BinaryField(db_column='_IDRRef', unique=True)
    db_id_doc661 = models.TextField(db_column='_Fld7931_RRRef')

    date_of_formation = models.DateField(db_column='date_of_formation')
    date_of_payment = models.DateTimeField(db_column='_Fld7905')
    date_of_shipment = models.DateTimeField(db_column='_Fld7906')
    shipment = models.DecimalField(max_digits=15, decimal_places=2)
    payment = models.DecimalField(max_digits=15, decimal_places=2)

    number = models.CharField(db_column='_Number', max_length=11, db_collation='Cyrillic_General_CI_AS')

    buyer = models.ForeignKey(
        'BuyerBook',
        to_field='db_id',
        db_column='_Fld7912RRef',
        on_delete=models.CASCADE,
        related_name='orders'
    )

    cost = models.DecimalField(db_column='_Fld7924', max_digits=15, decimal_places=2)
    delivery = models.TextField(db_column='_Fld7901', db_collation='Cyrillic_General_CI_AS')
    responsible = models.TextField(db_column='_Fld7917RRef')
    comments = models.TextField(db_column='_Fld7911', db_collation='Cyrillic_General_CI_AS')

    class Meta:
        managed = False
        db_table = '_document400'
        verbose_name = 'Заказы покупателей'  # Имя модели в админке
        verbose_name_plural = 'Заказы покупателей'  # Множественное число в админке

    def formatted_number(self):
        """Удаляет префикс букв и ведущие нули из номера."""
        import re
        number = re.sub(r'^[^\d]+0*', '', self.number)  # Удаляет все символы перед цифрами и ведущие нули
        return f'{number}'

    def to_json(self):
        return {
            # "id": str(self.pk),
            "number": self.number,
            # "date": self.date.isoformat(),
            "buyer": self.buyer,
            # "total": str(self.total),
        }

# Контрагенты
class BuyerBook(models.Model):
    db_id = models.BinaryField(db_column='_IDRRef', unique=True)
    description = models.CharField(db_column='_Description', max_length=100, db_collation='Cyrillic_General_CI_AS')
    inn_code = models.CharField(db_column='_Fld2682', max_length=12, db_collation='Cyrillic_General_CI_AS', blank=True, null=True)
    full_name = models.TextField(db_column='_Fld2676', db_collation='Cyrillic_General_CI_AS', blank=True, null=True)
    field_code = models.CharField(db_column='_Code', max_length=9, db_collation='Cyrillic_General_CI_AS')

    class Meta:
        managed = False
        db_table = '_reference141'
        verbose_name = 'Контрагенты'  # Имя модели в админке
        verbose_name_plural = 'Контрагенты'  # Множественное число в админке

    def __str__(self):
        return self.description or "Неизвестный покупатель"

# Реализации
class RealizationBook(models.Model):
    db_id = models.BinaryField(db_column='_IDRRef', unique=True)
    number = models.CharField(db_column='_Number', max_length=11, db_collation='Cyrillic_General_CI_AS')
    date_of = models.DateTimeField(db_column='_Date_Time')

    realizations = models.ForeignKey(
        'OrdersBook',
        to_field='db_id',
        db_column='_Fld17829_RRRef',
        on_delete=models.CASCADE,
        related_name='realizations'
    )

    class Meta:
        managed = False
        db_table = '_Document617'
        verbose_name = 'Реализации'  # Имя модели в админке
        verbose_name_plural = 'Реализации'  # Множественное число в админке

# Состав "Заказа покупателя"
class OrderList(BasicUnitMixin, models.Model):

    order = models.ForeignKey( # Связь с OrdersBook (_Document400: Заказы покупателей)
        'OrdersBook',
        to_field='db_id',
        db_column='_Document400_IDRRef',
        on_delete=models.CASCADE,
        related_name='order_items'
    )

    nomenclature = models.ForeignKey( # Связь с NomencBook (_Reference175: Номенклатура)
        'my_erp.NomencBook',
        to_field='db_id',
        db_column='_Fld7944RRef',
        on_delete=models.CASCADE,
        related_name='order_lines'
    )

    line_number = models.DecimalField(db_column='_LineNo7938', max_digits=5, decimal_places=0)
    quantity = models.DecimalField(db_column='_Fld7941', max_digits=15, decimal_places=3) # Кол-во

    price = models.DecimalField(db_column='_Fld7955', max_digits=5, decimal_places=2) # Стоимость за 1 шт. без НДС
    amount = models.DecimalField(db_column='_Fld7950', max_digits=15, decimal_places=2) # Сумма без НДС
    amount_nalog = models.DecimalField(db_column='_Fld7953', max_digits=15, decimal_places=2) # размер НДС

    @property
    def sum_total(self): # Сумма с НДС
        return (self.amount or 0) + (self.amount_nalog or 0)

    class Meta:
        managed = False
        db_table = '_Document400_VT7937'
        verbose_name = 'Состав заказа покупателя'  # Имя модели в админке
        verbose_name_plural = 'Состав заказа покупателя'  # Множественное число в админке

# Регистр сведений "таблица-связь" номенклатура:спецификация
class InfoRg23775(models.Model):
    name_nomenc = models.ForeignKey(
        'my_erp.NomencBook',
        to_field='db_id',
        db_column='_Fld23776RRef',
        on_delete=models.CASCADE,
        related_name='info_records'
    )

    sp_idrref = models.ForeignKey(
        'SpecList',
        to_field='reference259_idrref',
        on_delete=models.CASCADE,
        db_column='_Fld23779RRef',
        related_name='info_record'
    )

    class Meta:
        managed = False
        db_table = '_InfoRg23775'
        verbose_name = 'Регистр сведений - Совпадение номенклатура:спецификация'  # Имя модели в админке
        verbose_name_plural = 'Регистр сведений - Совпадение номенклатура:спецификация'  # Множественное число в админке

# Регистр сведений - Список Комплектующих номенклатуры
class Inforg23220(BasicUnitMixin, models.Model):
    name_nomenc = models.ForeignKey( # IDRRef таблицы  dbo._Reference175 - искомая номенклатура
        'my_erp.NomencBook',
        to_field='db_id',
        db_column='_Fld23221RRef',
        on_delete=models.CASCADE,
        related_name='name_for_23220'
    )

    nomenclature = models.ForeignKey( # IDRRef таблицы  dbo._Reference175 - то что входит в состав комплектующих
        'my_erp.NomencBook',
        to_field='db_id',
        db_column='_Fld23223RRef',
        on_delete=models.CASCADE,
        related_name='structure_for_23220'
    )

    quantity = models.DecimalField(db_column='_Fld23225', max_digits=15, decimal_places=3)  # Количество

    class Meta:
        managed = False
        db_table = '_InfoRg23220'
        verbose_name = 'Регистр сведений - Список Комплектующих номенклатуры'  # Имя модели в админке
        verbose_name_plural = 'Регистр сведений - Список Комплектующих номенклатуры'  # Множественное число в админке

# Состав спецификаций
class SpecList(BasicUnitMixin, models.Model):
    reference259_idrref = models.BinaryField(db_column='_Reference259_IDRRef', unique=True)  # id поля _Fld23779RRef спецификации из _InfoRg23775
    nomenclature = models.ForeignKey(  # Связь с NomencBook (_Reference175: Номенклатура)
        'my_erp.NomencBook',
        to_field='db_id',
        db_column='_Fld4125_RRRef',
        on_delete=models.CASCADE,
        related_name='sp_items'
    )

    line_number = models.DecimalField(db_column='_LineNo4123', max_digits=5, decimal_places=0)  # номер строки
    quantity = models.DecimalField(db_column='_Fld4127', max_digits=15, decimal_places=3)  # Количество
    # fld4134rref = models.TextField(db_column='_Fld4134RRef')  # Вид воспроизводства - надо ли?

    @classmethod
    def get_latest_specs(cls, db_id):
        """
            Возвращает последнюю спецификацию по максимальному id InfoRg23775
            для заданной номенклатуры db_id.
        """

        # 1. Получаем запись с максимальным id по переданному db_idфыв
        latest_info = InfoRg23775.objects.filter(name_nomenc=db_id).order_by('-id').first()

        if not latest_info:
            return cls.objects.none()

        # 2. Получаем значение sp_idrref из этой записи
        latest_sp_idrref = latest_info.sp_idrref_id  # id будет в BinaryField

        # 3. Возвращаем спецификацию, связанную с этим sp_idrref
        return cls.objects.filter(reference259_idrref=latest_sp_idrref).select_related('nomenclature')

    class Meta:
        managed = False
        db_table = '_Reference259_VT4122'
        verbose_name = 'Состав спецификаций'  # Имя модели в админке
        verbose_name_plural = 'Состав спецификаций'  # Множественное число в админке


