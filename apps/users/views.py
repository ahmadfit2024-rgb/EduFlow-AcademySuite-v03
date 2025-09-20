from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class UserManagementView(LoginRequiredMixin, TemplateView):
    """
    Provides the main interface for administrators to manage all users.
    Handles initial page load and HTMX-powered search/filter requests.
    """
    template_name = 'users/user_management.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q', '')
        users = CustomUser.objects.all().order_by('-date_joined')
        if search_query:
            users = users.filter(
                Q(username__icontains=search_query) |
                Q(full_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        context['users'] = users
        context['search_query'] = search_query
        context['is_search'] = bool(search_query)
        return context

    def get(self, request, *args, **kwargs):
        if request.htmx:
            self.template_name = 'partials/_user_list.html'
        return super().get(request, *args, **kwargs)

class UserCreateView(LoginRequiredMixin, CreateView):
    """
    View for an admin to create a new user.
    """
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user_management')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Add New User"
        return context

class UserUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for an admin to update an existing user's details.
    """
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user_management')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edit User"
        return context

class UserDeleteView(LoginRequiredMixin, DeleteView):
    """
    Handles the deletion of a user. Responds to HTMX requests.
    """
    model = CustomUser
    success_url = reverse_lazy('users:user_management')
    
    # For HTMX requests, we don't need a confirmation page, 
    # the modal serves as confirmation.
    def get(self, request, *args, **kwargs):
        # Redirect GET requests to the main management page
        return redirect(self.success_url)

    def post(self, request, *args, **kwargs):
        # We need to get the object before deleting to have access to its data
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()

        # For HTMX requests, we trigger events instead of redirecting
        if request.htmx:
            response = self.render_to_response({})
            # This custom event will be picked up by the user management page to reload the list
            response['HX-Trigger'] = 'userDeleted'
            # This will trigger the global toast notification
            response['HX-Trigger-Detail'] = '{"message": "User has been deleted successfully."}'
            return response

        return redirect(success_url)