from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate


def create_admin_one(sender, **kwargs):
    #Import inside the function as causes an error when before the function
    from payapp.models import UserAccount

    User = get_user_model()
    #Create initial admin1 account, only if it doesn't already exist
    if not User.objects.filter(username="admin1").exists():
        user = User.objects.create_superuser(username="admin1", email="admin1@admin1.com", password="admin1")
        #Give the admin account default payment attributes
        UserAccount.objects.get_or_create(user=user, defaults={"currency": "GBP", "balance": 500.00})

class PayappadminConfig(AppConfig):
    name = "payappadmin"

    def ready(self):
        #Runs automatically after calling migrations
        post_migrate.connect(create_admin_one, sender=self)