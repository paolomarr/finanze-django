from django.forms import ModelForm, ModelChoiceField
from django.forms.widgets import Input, HiddenInput, Select
from .models import Movement, AssetBalance, Category
from django.contrib.auth.models import User
from django.utils.translation import gettext as _


class MyDateTimeInputWidget(Input):
    input_type = "datetime-local"

class NewMovementForm(ModelForm):
    
    class Meta:
        model = Movement
        fields = [
            'date',
            'abs_amount',
            'description',
            'category',
            'subcategory'
        ]
        localized_fields = fields
        labels = {f:_(f.replace("_", " ").title()) for f in fields}
        widgets = {
            'date': MyDateTimeInputWidget(),
        }

class NewAssetsBalanceForm(ModelForm):
    class Meta:
        model = AssetBalance
        fields = '__all__'
        localized_fields = '__all__'
        widgets = {
            'date': MyDateTimeInputWidget(),
            'balance': HiddenInput()
        }