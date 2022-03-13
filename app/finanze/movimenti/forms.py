from django.forms import ModelForm
from django.forms.widgets import Input, HiddenInput
from .models import Movement, AssetBalance


class MyDateTimeInputWidget(Input):
    input_type = "datetime-local"


class NewMovementForm(ModelForm):

    class Meta:
        model = Movement
        fields = '__all__'
        widgets = {
            'date': MyDateTimeInputWidget()
        }

class NewAssetsBalanceForm(ModelForm):
    class Meta:
        model = AssetBalance
        fields = '__all__'
        widgets = {
            'date': MyDateTimeInputWidget(),
            'balance': HiddenInput()
        }