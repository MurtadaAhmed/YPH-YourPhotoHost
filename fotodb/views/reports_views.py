from django.shortcuts import get_object_or_404

from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.shortcuts import redirect

# Custom:
from fotodb.models import Image, Report
from fotodb.forms import ReportForm


def moderators_check(user):
    """
    function to check if the logged-in user belong to moderators group. used in:
    ImageDetailView, ImageDeleteView, AlbumDeleteView, ImageEditView
    """
    return user.groups.filter(name='Moderators').exists()


class ReportImageView(LoginRequiredMixin, CreateView):
    """
    Allows users to report an image for inappropriate content or violations.
    Users can provide a detailed report by filling out the reporting form.
    """
    template_name = "report_image.html"
    form_class = ReportForm

    def get_context_data(self, **kwargs):
        """
        Retrieves the context data for rendering the reporting form.
        Adds the image associated with the report to the context.
        """
        context = super().get_context_data(**kwargs)
        context['image'] = get_object_or_404(Image, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        """
        Handles the submission of the reporting form and saves the report.
        If no existing report exists for the image, a new report is created.
        """
        image = get_object_or_404(Image, pk=self.kwargs['pk'])
        existing_report = Report.objects.filter(image=image).exists()
        if not existing_report:
            report = form.save(commit=False)
            image.is_private = True
            image.save()
            report.image = image
            report.reporter = self.request.user
            report.save()

        return redirect('recent')


class ReportedImagesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Displays a list of reported images, accessible by superusers and moderators.
    Superusers and moderators can view and take actions on reported images, such as deleting images or canceling reports.
    """
    template_name = 'reported_images.html'
    model = Report
    context_object_name = 'reports'

    def test_func(self):
        """
        Checks if the logged-in user is a superuser or a moderator.
        """
        return self.request.user.is_superuser or moderators_check(self.request.user)

    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)

        if 'delete' in request.POST:
            # Delete the reported image and the associated report
            report.image.delete()
            report.delete()
        elif 'cancel' in request.POST:
            # Delete the report without taking any action on the image
            report.image.is_private = False
            report.image.save()
            report.delete()

        return redirect('reported_images')
