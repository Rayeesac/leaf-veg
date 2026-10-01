from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


class HomepageAdminSite(AdminSite):
    """After a successful admin login, go to the homepage instead of /admin/."""

    def login(self, request, extra_context=None):
        # Redirect to the site login page, not the admin login page
        from django.shortcuts import redirect
        return redirect('/login/')


# Replace the global admin site instance
admin.site.__class__ = HomepageAdminSite

urlpatterns = [
    # Site-branded login / logout
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('', include('catalog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
