from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden

from apps.invitations.models import MemberInvitation
from apps.invitations.forms import InvitationResponseForm


# at this point users are possibly unauthenticated
def invitation_landing(request, code):
    inv = get_object_or_404(MemberInvitation, pk=code)
    if not inv.is_valid:
        return render(request, 'invitations/not_available.html')
    if request.user == inv.project.owner:  # owner clicked own link
        return HttpResponseForbidden("User action not permitted.")
    if not request.user.is_authenticated:
        return render(request, 'invitations/landing_not_logged_in.html', {
            'project': inv.project, 'return_url': inv.landing_url})
    else:
        # logged in, so just ask if accept
        form = InvitationResponseForm()
        form.helper.form_action = reverse_lazy('invitation-respond', kwargs={'code': code})
        ctx = {'form': form}
        return render(request, 'invitations/landing_logged_in.html', ctx)

def invitation_respond(request, code):
    inv = get_object_or_404(MemberInvitation, pk=code)
    if not inv.is_valid:
        return render(request, 'invitations/not_available.html')
    if request.user == inv.project.owner:  # owner clicked own link
        return HttpResponseForbidden("User action not permitted.")
    if not request.user.is_authenticated:
        return redirect(inv.landing_url)
    if request.method == 'POST' and request.POST.get('yes'):
        inv.accept(request.user)
        inv.save()
        return redirect(inv.project.url)
    else:
        HttpResponseForbidden("User action not permitted.")
