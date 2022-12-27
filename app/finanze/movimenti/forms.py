from django.forms import ModelForm, ModelChoiceField
from django.forms.widgets import Input, HiddenInput, Select
from .models import Movement, AssetBalance, Category
from django.utils.translation import gettext as _
from django.contrib.auth.models import User


class MyDateTimeInputWidget(Input):
    input_type = "datetime-local"

class NewMovementForm(ModelForm):
    
    class Meta:
        model = Movement
        fields = '__all__'
        widgets = {
            'date': MyDateTimeInputWidget(),
        }

class NewAssetsBalanceForm(ModelForm):
    class Meta:
        model = AssetBalance
        fields = '__all__'
        widgets = {
            'date': MyDateTimeInputWidget(),
            'balance': HiddenInput()
        }