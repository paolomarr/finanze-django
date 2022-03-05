from django.forms import ModelForm
from django.forms.widgets import Input
from .models import Movement


class MyDateTimeInputWidget(Input):
    input_type = "datetime-local"


class NewMovementForm(ModelForm):

    class Meta:
        model = Movement
        fields = '__all__'
        widgets = {
            'date': MyDateTimeInputWidget()
        }
