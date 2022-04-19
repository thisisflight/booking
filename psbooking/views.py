from django.shortcuts import render


def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)


def page_permission_denied_view(request, exception):
    return render(request, '403.html', status=403)


def page_server_error_view(request, exception):
    return render(request, '500.html', status=500)
