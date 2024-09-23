from django import forms
from .models import Profile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button
from allauth.account import forms as aaforms

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["institution", "location"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("Save", "save"))
        self.helper.add_input(
            Button(
                "Cancel", "Cancel", css_class="btn", onclick="javascript:history.back()"
            )
        )


class LoginForm(aaforms.LoginForm):

    def login(self, *args, **kwargs):
        # Add your own processing here.

        # You must return the original result.
        return super(LoginForm, self).login(*args, **kwargs)


class SignupForm(aaforms.SignupForm):

    def save(self, request):
        user = super(SignupForm, self).save(request)
        # Add your own processing here.

        # You must return the original result.
        return user
