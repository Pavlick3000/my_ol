from django import forms
from my_erp.models import NomencBook, ProductionTypeBook, BasicUnitBook, NomencUnitBook
import uuid


class NomencBookForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-3 py-2 mb-4 border rounded', 'placeholder': 'Введите наименование'
    }))
    type_of_reproduction = forms.ChoiceField(widget=forms.Select(attrs={
        'class': 'block mb-2 text-sm font-medium text-gray-700'
    }))
    basic_unit = forms.ChoiceField(widget=forms.Select(attrs={
        'class': 'block mb-2 text-sm font-medium text-gray-700'
    }))

    class Meta:
        model = NomencBook
        exclude = ['db_id']
        fields = ('name','type_of_reproduction', 'basic_unit')  # Вы можете указать конкретные поля, если нужно

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Определяем поле выбора для type_of_reproduction
        self.fields['type_of_reproduction'] = forms.ChoiceField(
            choices=[(prod.reproduction.hex().upper(), prod.name) for prod in ProductionTypeBook.objects.filter(reproduction__isnull=False).order_by('-id')],
            required=False,
            label="Тип воспроизводства")

        # Определяем поле выбора для basic_unit
        self.fields['basic_unit'] = forms.ChoiceField(
            choices=[(unit.db_id.hex().upper(), unit.name) for unit in BasicUnitBook.objects.all()],
            required=False,
            label="Базовая единица")

    def clean_type_of_reproduction(self):
        data = self.cleaned_data.get('type_of_reproduction')
        if data is not None:
            return bytes.fromhex(data)
        return None

    def clean_basic_unit(self):
        data = self.cleaned_data.get('basic_unit')
        if data:
            return bytes.fromhex(data)
        return None

    def save(self, commit=True):
        self.instance.write()

        # Проверяем, существует ли запись в NomencUnitBook
        if not NomencUnitBook.objects.filter(field_ownerid_rrref=self.instance.db_id).exists():
            print("попали сюда! Проверяем, существует ли запись в NomencUnitBook")
            # Если записи нет, создаем новую запись в NomencUnitBook
            unit_record = NomencUnitBook.objects.create(
                db_id=uuid.uuid4().bytes,  # Генерация нового UUID для db_id в формате bytes
                field_ownerid_rrref=self.instance.db_id,  # Используем db_id из NomencBook
                field_fld2487rref=self.instance.basic_unit,  # Используем basic_unit из NomencBook
                field_description=BasicUnitBook.objects.get(db_id=self.instance.basic_unit).name,
                # Получаем name из BasicUnitBook
                field_code=NomencUnitBook.generate_new_code(),  # Генерация нового значения для field_code
            )

            self.instance.basic_unit_1 = unit_record.db_id
            self.instance.basic_unit_2 = unit_record.db_id

        # Сохраняем изменения в NomencBook
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance
