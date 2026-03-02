from django.conf import settings
from unfold.sites import UnfoldAdminSite


class CustomAdminSite(UnfoldAdminSite):
    site_header = f'{settings.PROJECT_NAME} Admin'
    site_title = f'{settings.PROJECT_NAME} Portal'
    index_title = f'Welcome to {settings.PROJECT_NAME} admin panel'

    def get_urls(self):
        urls = super().get_urls()
        return urls


admin_site = CustomAdminSite(name='admin_site')
