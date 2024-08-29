from django.shortcuts import get_object_or_404, render, redirect
from apps.projects.models import Membership

# at this point users are possibly unauthenticated
def invitation_landing(request, code):
    mship = get_object_or_404(Membership, invitation_code=code)
    if mship.status != 'invited':
        return render(request, 'invitations/not_available.html')
    if mship.invitation_email.lower() == mship.project.owner.email.lower():
        # project owner clicked invitation link
        return redirect(mship.project.url())
    if not request.user.is_authenticated:
        return render(request, 'invitations/landing_not_logged_in.html', {
            'project': mship.project, 'return_url': mship.invitation_landing_url})
    else:
        # logged in, so just ask if accept
        return render(request, 'invitations/landing_logged_in.html')
