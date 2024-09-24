from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3
from django.conf import settings

from .models import (
    Project,
    Question,
    Bot,
    ConsentLetter,
    Interview,
    Transcript,
    MemberInvitation,
)

# another possibility: https://stackoverflow.com/a/56719980


def cancel():
    return Button(
        "Cancel", "Cancel", css_class="btn", onclick="javascript:history.back()"
    )


def save():
    return Submit("Save", "save")


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "research_aims", "funding"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].widget.attrs["rows"] = 3
        self.fields["research_aims"].widget.attrs["rows"] = 3
        self.fields["funding"].widget.attrs["rows"] = 2
        self.helper = FormHelper()
        self.helper.add_input(save())
        self.helper.add_input(cancel())


class MemberInvitationForm(forms.ModelForm):
    class Meta:
        model = MemberInvitation
        fields = ["name", "email", "role"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(save())
        self.helper.add_input(cancel())


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["question", "is_enabled"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["question"].widget.attrs["rows"] = 2
        self.helper = FormHelper()
        self.helper.add_input(save())
        self.helper.add_input(cancel())


class BotForm(forms.ModelForm):
    class Meta:
        model = Bot
        fields = [
            "name",
            "description",
            "prompt",
            "version",
            "aimodel",
            "config",
            "opening_user_statement",
            "end_string",
            "consent_letter",
            "status",
            "allow_public",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].widget.attrs["rows"] = 3
        self.fields["prompt"].widget.attrs["rows"] = 20
        self.fields["config"].widget.attrs["rows"] = 2
        self.helper = FormHelper()
        self.helper.add_input(save())
        self.helper.add_input(cancel())


class ConsentLetterForm(forms.ModelForm):
    class Meta:
        model = ConsentLetter
        fields = ["name", "short_md", "letter_md"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["short_md"].widget.attrs["rows"] = 4
        self.helper = FormHelper()
        self.helper.add_input(save())
        self.helper.add_input(cancel())


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ["bot", "subject_name", "subject_email"]

    subject_email = forms.EmailField(label="Recipient email", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(save())
        self.helper.add_input(cancel())


class ManualTranscriptForm(forms.ModelForm):
    class Meta:
        model = Transcript
        fields = ["subject_name", "description", "full_text"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].widget.attrs["rows"] = 3
        self.helper = FormHelper()
        self.helper.add_input(save())
        self.helper.add_input(cancel())


class InvitationResponseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("yes", "Yes, accept"))


class PublicConsentForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = [
            "subject_name",
            "subject_email",
            "has_consented",
            "followup_consented",
        ]

    subject_name = forms.CharField(label="Your name", required=True)
    subject_email = forms.CharField(label="Your email address", required=False)
    has_consented = forms.BooleanField(
        label="I consent to participating in this study", required=True
    )
    followup_consented = forms.BooleanField(
        label="The investigators may contact me for follow-up", required=False
    )
    if not (settings.DEBUG or settings.TESTING):
        # https://pypi.org/project/django-recaptcha/
        captcha = ReCaptchaField(widget=ReCaptchaV3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit("proceed", "Proceed", css_class="btn btn-primary d-grid w-100")
        )


class InterviewConsentForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ["has_consented", "followup_consented"]

    has_consented = forms.BooleanField(
        label="I consent to participating in this study", required=True
    )
    followup_consented = forms.BooleanField(
        label="The investigators may contact me for follow-up", required=False
    )
    # no captcha because this is not a public url

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit("proceed", "Proceed", css_class="btn btn-primary d-grid w-100")
        )


class ExportInterviewsForm(forms.Form):
    what = forms.ChoiceField(
        label="Download",
        choices=[("interviews", "Interviews"), ("test", "Test interviews")],
        initial="interviews",
        required=True,
    )
    include_metadata = forms.BooleanField(
        label="Include interview metadata", initial=True, required=False
    )
    acknowledge = forms.BooleanField(
        label="I understand my ethical and legal obligations to safeguard the security of interview material",
        required=True,
        initial=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("Export", "export"))
        self.helper.add_input(cancel())


class LundSurveyForm(forms.Form):
    ACADEMIC_CHOICES = [
        ("public", "Yes, and I am employed by a public university"),
        ("private", "Yes, and I am employed by a private institution"),
        ("independent", "Yes, I am an independent researcher"),
        ("no", "No, I am not an academic"),
    ]
    is_academic = forms.ChoiceField(
        label="Are you an academic?",
        required=True,
        choices=ACADEMIC_CHOICES,
        widget=forms.Select(),
    )
    academic_age = forms.IntegerField(
        label="Your academic age",
        required=False,
        widget=forms.NumberInput(
            attrs={"placeholder": "Number of years post PhD or relevant qualification"}
        ),
    )
    discipline = forms.CharField(
        label="Main academic discipline",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "e.g. Sociology or Economics"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("Continue", "continue"))
