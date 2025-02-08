# apps/core/views.py
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'core/home.html'
    def get_template_names(self):
        if not self.request.user.is_authenticated:
            return ['core/landing.html']
        return [self.template_name]