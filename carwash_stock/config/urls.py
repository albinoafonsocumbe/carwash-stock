"""
URL configuration for carwash_stock project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView, TemplateView
from django.conf import settings
from django.conf.urls.static import static


class LandingView(TemplateView):
    template_name = 'landing.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('stock/', include('stock.urls')),
    path('services/', include('services.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('reports/', include('reports.urls')),
    path('lavagens/', include('lavagens.urls')),
    path('', LandingView.as_view(), name='landing'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
