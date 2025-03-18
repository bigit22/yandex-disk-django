import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.core.cache import cache
from typing import List, Dict, Any, Optional


def get_files(public_key: str, access_token: str) -> List[Dict[str, Any]]:
    """
        Fetches files from a public Yandex.Disk folder.

        Args:
            public_key (str): Public key for the folder.
            access_token (str): OAuth access token.

        Returns:
            List[Dict[str, Any]]: List of files or empty list on failure.
    """
    headers = {
        'Authorization': f'OAuth {access_token}',
    }
    url = f'https://cloud-api.yandex.net/v1/disk/resources/public?public_key={public_key}'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('items', [])
    return []


def oauth_authorize() -> HttpResponse:
    """
        Redirects to Yandex authorization page.

        Returns:
            HttpResponse: Redirect response.
    """
    auth_url = (
        f'https://oauth.yandex.com/authorize?response_type=code'
        f'&client_id={settings.YA_CLIENT_ID}'
        f'&redirect_uri={settings.YA_REDIRECT_URI}'
        f'&scope=cloud_api:disk.read'
    )
    return redirect(auth_url)


def oauth_callback(request: HttpRequest) -> HttpResponse:
    """
        Handles OAuth callback and retrieves access token.

        Args:
            request: HTTP request containing the authorization code.

        Returns:
            HttpResponse: Redirect or error response.
    """
    code: Optional[str] = request.GET.get('code')
    if not code:
        print('We have no token!')

    token_url = 'https://oauth.yandex.com/token'
    body = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': settings.YA_CLIENT_ID,
        'client_secret': settings.YA_CLIENT_SECRET,
        'redirect_uri': settings.YA_REDIRECT_URI,
    }

    try:
        response = requests.post(token_url, data=body)
        response_data = response.json()

        if response.status_code == 200:
            access_token = response_data.get('access_token')
            request.session['access_token'] = access_token
            return render(request, 'disk_app/index.html')
        else:
            print('Failed to obtain access token. Response:', response_data)
            return HttpResponse(
                'Failed to obtain access token: ' + response_data.get('error_description', ''),
                status=400
            )
    except requests.RequestException as e:
        print('Error occurred while communicating with the OAuth provider:', str(e))
        return HttpResponse('Error communicating with the OAuth provider', status=500)


def index(request: HttpRequest) -> HttpResponse:
    """
        Renders the main page.

        Args:
            request: HTTP request.

        Returns:
            HttpResponse: Rendered main page response.
    """
    return render(request, 'disk_app/index.html')


def list_files(request: HttpRequest) -> HttpResponse:
    """
    Lists files from a public folder.

    Args:
        request: HTTP request containing the access token and public key.

    Returns:
        HttpResponse: Rendered file list or redirect to main page.
    """
    access_token: Optional[str] = request.session.get('access_token')

    if not access_token:
        return oauth_authorize()

    if request.method == 'POST':
        public_key: str = request.POST.get('public_key')
        cache_key = f'file_list_{public_key}_{access_token}'
        files: List[Dict[str, Any]] = cache.get(cache_key)

        if files is None:
            files = get_files(public_key, access_token)
            cache.set(cache_key, files, 300)

        return render(request, 'disk_app/list_files.html', {
            'files': files,
            'public_key': public_key,
        })

    if request.method == 'GET':
        public_key: str = request.GET.get('public_key')
        media_type: str = request.GET.get('media_type', '')
        cache_key = f'file_list_{public_key}_{access_token}'
        files: List[Dict[str, Any]] = cache.get(cache_key)

        if files is None:
            files = get_files(public_key, access_token)
            cache.set(cache_key, files, 300)

        if media_type:
            files = [f for f in files if f.get('media_type') == media_type]

        return render(request, 'disk_app/list_files.html', {
            'files': files,
            'public_key': public_key,
        })

    return redirect('index')


@require_POST
def download_file(request: HttpRequest) -> HttpResponse:
    """
        Downloads a specified file.

        Args:
            request: HTTP request containing the file URL.

        Returns:
            HttpResponse: File download response or error message.
    """
    file_url: Optional[str] = request.POST.get('file_url')

    response = requests.get(file_url)

    if response.status_code == 200:
        download_response = HttpResponse(response.content)
        download_response['Content-Disposition'] = f'attachment; filename={file_url.split("/")[-1]}'
        download_response['Content-Type'] = 'application/octet-stream'
        return download_response

    return HttpResponse('Error occurred while downloading file.', status=response.status_code)