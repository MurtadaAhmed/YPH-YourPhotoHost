from django.views.generic import TemplateView


class TempMainView(TemplateView):
    # website home page view
    template_name = 'home.html'