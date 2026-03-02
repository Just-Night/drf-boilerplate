from django.contrib.auth import get_user_model

from apps.admin.site import admin_site
from apps.admin import model_admin as main_model_admin


admin_site.register(get_user_model(), main_model_admin.UserAdmin)
