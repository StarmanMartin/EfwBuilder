import requests
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

from Adminview.models import ElnConnection
from sdc_user.models import CustomUserManager

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):


        try:
            instance = ElnConnection.get_active()
            session = requests.Session()

            headers = {"Authorization": "Bearer %s" % instance.token}
            res = session.get('%s/api/v1/admin/disk' % instance.url, headers=headers)
            if res.status_code != 201 and res.status_code != 200:
                return
        except:
            try:
                if not ElnConnection.activate_connection(username, password):
                    return
            except:
                return

        try:
            user = UserModel.objects.get(Q(username__iexact=username))
        except UserModel.MultipleObjectsReturned:
            user = UserModel.objects.filter(Q(username__iexact=username) ).order_by('id').first()
        except:
            user = UserModel.objects.create_superuser(username, password)
        return user

