
from django.db import models


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

class OrderList(models.Model):

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