from django import forms
from django.urls import reverse_lazy

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from crispy_bootstrap5.bootstrap5 import FloatingField

from .models import Enquiry


class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ["email", "name", "message"]

    email = forms.EmailField(label="Work email", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse_lazy('enquiry_partial')
        self.helper.form_method = 'POST'
        #self.helper.form_id = 'university-form'
        self.helper.attrs = {
            'hx-post': reverse_lazy('enquiry_partial'),
            'hx-target': '#enquiry-card',
            'hx-swap': 'outerHTML'
        }
        self.helper.layout = Layout(
            Div(
                Div(
                    FloatingField("name"),
                    css_class="col-md-6"
                ),
                Div(
                    FloatingField("email"),
                    css_class="col-md-6"
                ),
                Div(
                    FloatingField("message", template='_bs5_floating_field_h_200.html'),
                    css_class="col-12"
                ),
                css_class="row g-5"
            ),
            Submit("send", "Send enquiry", css_class="mt-5")
        )
