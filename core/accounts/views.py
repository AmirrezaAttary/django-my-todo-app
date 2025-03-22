from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.shortcuts import redirect
from .forms import CustomUserCreationForm  # فرم سفارشی را ایمپورت کنید
from accounts.task import sendEmail
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import cache_page
import requests
from django.conf import settings

class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    fields = (
        "email",
        "password",
    )  # تغییر به 'email' چون مدل شما از username استفاده نمی‌کند
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("todo:task-list")


class RegisterPage(FormView):
    template_name = "accounts/register.html"
    form_class = CustomUserCreationForm  # استفاده از فرم سفارشی
    redirect_authenticated_user = True
    success_url = reverse_lazy("todo:task-list")

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("todo:task-list")
        return super(RegisterPage, self).get(*args, **kwargs)


def send_email(request):
    sendEmail.delay()
    return HttpResponse("Email sent successfully.")


@cache_page(60 * 20)  # کش کردن پاسخ به مدت ۲۰ دقیقه
def weather_view(request, city="تهران"):
    api_key = settings.OPENWEATHER_API_KEY  # از settings یا مستقیماً کلید را قرار دهید
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=fa'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        result = {
            'city': data['name'],
            'country': data['sys']['country'],
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed']
        }
        return JsonResponse(result)
    else:
        return JsonResponse({'error': 'شهر یافت نشد'}, status=404)