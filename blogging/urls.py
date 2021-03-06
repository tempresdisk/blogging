from django.contrib import admin
from django.urls import include, path, re_path  # re_path for ngrok
from django.conf.urls import handler404, handler500
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # for ngrok
from django.views.static import serve  # for ngrok


handler404 = "posts.views.page_not_found" # noqa
handler500 = "posts.views.server_error" # noqa

urlpatterns = [
    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path("administration/", admin.site.urls),
    path("", include("posts.urls")),
    path("about/", include("about.urls", namespace='about')),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)

urlpatterns += staticfiles_urlpatterns()  # for ngrok
urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve,
                {'document_root': settings.MEDIA_ROOT, }), ]  # for ngrok
