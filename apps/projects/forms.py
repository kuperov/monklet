from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button

from .models import Project, Question, Bot, ConsentLetter, Interview
from apps.invitations.models import MemberInvitation

# another possibility: https://stackoverflow.com/a/56719980

def cancel():
    return Button("Cancel", "Cancel", css_class="btn", onclick="javascript:history.back()")

def save():
    return Submit("Save", "save")

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "research_aims", "funding"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        self.helper = FormHelper()
        self.helper.add_input(save())
        self.helper.add_input(cancel())

class BotForm(forms.ModelForm):
    class Meta:
        model = Bot
        fields = [
            "name", "description", "prompt", "version", "aimodel", "end_string", "status", "allow_public"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(save())
        self.helper.add_input(cancel())


class ConsentLetterForm(forms.ModelForm):
    class Meta:
        model = ConsentLetter
        fields = [
            "name", "short_md", "letter_md"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(save())
        self.helper.add_input(cancel())


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ["bot", "subject_email", "subject_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(save())
        self.helper.add_input(cancel())
