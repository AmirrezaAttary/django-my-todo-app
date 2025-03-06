from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from todo.models import Task
from todo.forms import TodoUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

# Create your views here.

class TodoListView(LoginRequiredMixin,ListView):
    model = Task
    context_object_name = 'tasks'
    ordering = "-created_date"

class TodoCreateView(LoginRequiredMixin,CreateView):
    model = Task
    fields = ["title"]
    success_url = "/"
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TodoCreateView, self).form_valid(form)