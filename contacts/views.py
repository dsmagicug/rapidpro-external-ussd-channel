from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Contact


@login_required(login_url="/login/")
def contacts(request):
    if request.method == "GET":
        all_contacts = Contact.objects.all().order_by('-created_on')
        if len(all_contacts) == 0:
            all_contacts = None
        return render(
            request, "contacts/contacts.html",
            {"contacts": all_contacts}
        )
