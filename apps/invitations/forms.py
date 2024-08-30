from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button

class InvitationResponseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('yes', 'Yes, accept'))
        self.helper.add_input(Button('no', 'No, decline', css_class='btn btn-secondary'))
