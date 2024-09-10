from django import forms
from .models import Profile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["institution", "location"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("Save", "save"))
        self.helper.add_input(Button("Cancel", "Cancel", css_class="btn", onclick="javascript:history.back()"))
