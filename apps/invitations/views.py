from django.shortcuts import get_object_or_404, render, redirect
from apps.projects.models import Membership
from .forms import InvitationResponseForm
from django.urls import reverse_lazy
from django.http import HttpResponseBadRequest, HttpResponseForbidden


# at this point users are possibly unauthenticated
def invitation_landing(request, code):
    mship = get_object_or_404(Membership, invitation_code=code)
    if mship.status != 'invited':
        return render(request, 'invitations/not_available.html')
    if request.user == mship.project.owner:  # owner clicked own link
        return HttpResponseForbidden("User action not permitted.")
    if not request.user.is_authenticated:
        return render(request, 'invitations/landing_not_logged_in.html', {
            'project': mship.project, 'return_url': mship.invitation_landing_url})
    else:
        # logged in, so just ask if accept
        form = InvitationResponseForm()
        form.helper.form_action = reverse_lazy('invitation-respond', kwargs={'code': code})
        ctx = {'form': form}
        return render(request, 'invitations/landing_logged_in.html', ctx)

def invitation_respond(request, code):
    mship = get_object_or_404(Membership, invitation_code=code)
    if mship.status != 'invited':
        return render(request, 'invitations/not_available.html')
    if request.user == mship.project.owner:  # owner clicked own link
        return HttpResponseForbidden("User action not permitted.")
    if not request.user.is_authenticated:
        return redirect(mship.invitation_landing_url)
    if request.POST.get('yes'):
        mship.user = request.user
        mship.status = 'accepted'
        mship.save()
        return redirect(mship.project.url())
    elif request.POST.get('no'):
        mship.user = request.user
        mship.status = 'declined'
        mship.save()
        return redirect(reverse_lazy('profile'))
    else:
        raise HttpResponseBadRequest()
