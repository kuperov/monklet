from django import forms
from .models import Profile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button, Layout
from crispy_bootstrap5.bootstrap5 import FloatingField

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

    # login
    # password
    # remember

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            FloatingField("login"), FloatingField("password"), "remember"
        )
        self.helper.add_input(Submit("signin", "Sign in", css_class="d-grid w-100"))

    def login(self, *args, **kwargs):
        # custom processing
        return super(LoginForm, self).login(*args, **kwargs)


class SignupForm(aaforms.SignupForm):

    # email
    # password1
    # password2
    name = forms.CharField(
        min_length=5, max_length=100, label="Full name", required=True
    )
    institution = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            FloatingField("name"),
            FloatingField("email"),
            FloatingField("institution"),
            FloatingField("password1"),
            FloatingField("password2"),
        )
        self.helper.add_input(Submit("signup", "Sign up", css_class="d-grid w-100"))

    def save(self, request):
        user = super(SignupForm, self).save(request)
        user.name = self.cleaned_data["name"]
        user.save()
        _profile = Profile.objects.create(user=user)
        # TODO: download avatar
        return user


class ResetPasswordForm(aaforms.ResetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit("reset", "Reset password", css_class="d-grid w-100")
        )


class ResetPasswordKeyForm(aaforms.ResetPasswordKeyForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit("reset", "Change password", css_class="d-grid w-100")
        )
