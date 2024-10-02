from django import forms
from .models import NomencBook, ProductionTypeBook, BasicUnitBook

class NomencBookAdminForm(forms.ModelForm):
    class Meta:
        model = NomencBook
        fields = '__all__'  # Вы можете указать конкретные поля, если нужно

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Определяем поле выбора для type_of_reproduction
        self.fields['type_of_reproduction'] = forms.ChoiceField(
            choices=[(prod.reproduction.hex().upper(), prod.name) for prod in ProductionTypeBook.objects.all()],
            required=False,
            label="Тип воспроизводства")

        # Определяем поле выбора для basic_unit
        self.fields['basic_unit'] = forms.ChoiceField(
            choices=[(unit.db_id.hex().upper(), unit.name) for unit in BasicUnitBook.objects.all()],
            required=False,
            label="Базовая единица")

    def clean_type_of_reproduction(self):
        data = self.cleaned_data.get('type_of_reproduction')
        if data:
            return bytes.fromhex(data)
        return None

    def clean_basic_unit(self):
        data = self.cleaned_data.get('basic_unit')
        if data:
            return bytes.fromhex(data)
        return None
