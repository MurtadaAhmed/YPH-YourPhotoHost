
from django.conf import settings

from django.core.mail import send_mail

from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.views import View
from django.views.generic import TemplateView
from django.urls import reverse

# Custom:
from fotodb.forms import ContactForm


class ContactView(View):
    template_name = 'contact_form.html'

    def get(self, request, *args, **kwargs):
        form = ContactForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            subject = f'Contact Us Form from {name}'
            message = f'Name: {name}\nEmail: {email}\nMessage: {message}'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])

            user_subject = 'Thank you for contacting us!'
            user_message = 'Thank you for contacting us. We have received your message and will get back to you soon.'
            send_mail(user_subject, user_message, settings.DEFAULT_FROM_EMAIL, [email])

            return HttpResponseRedirect(reverse('contact_success'))

        return render(request, self.template_name, {'form': form})


class ContactSuccessView(TemplateView):
    template_name = 'contact_success.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({})

    def post(self, request, *args, **kwargs):
        return self.render_to_response({})
