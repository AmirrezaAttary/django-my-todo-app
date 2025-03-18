from django.shortcuts import redirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from todo.models import Task
from todo.forms import TodoUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import View

# Create your views here.


class TodoListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "tasks"
    ordering = "-created_date"

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class TodoCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = ["title"]
    success_url = "/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TodoCreateView, self).form_valid(form)


class TodoCompleteView(LoginRequiredMixin, View):
    model = Task
    success_url = "/"

    def get(self, request, *args, **kwargs):
        object = Task.objects.get(id=kwargs.get("pk"))
        object.complete = True
        object.save()
        return redirect(self.success_url)


class TodoDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = "/"


class TodoUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TodoUpdateForm
    success_url = "/"
