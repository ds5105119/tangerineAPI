from accounts.models import User
from accounts.utils import generate_handle
from profiles.models import Profile

try:
    from allauth.account.adapter import DefaultAccountAdapter
    from allauth.account.adapter import get_adapter as get_account_adapter
    from allauth.account.utils import user_email
    from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
    from allauth.utils import valid_email_or_none
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")


class AccountAdapter(DefaultAccountAdapter):
    """
    Custom Account Adapter(Dummy)
    Adapter for custom accounts, but IIHUS will not provide normal login.
    """

    pass


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom Social Account Adapter
    Override some methods to use the Profile model
    https://docs.allauth.org/en/latest/account/advanced.html
    """

    def pre_social_login(self, request, sociallogin):
        # user_data = sociallogin.account.extra_data
        pass

    def save_user(self, request, sociallogin, form=None):
        user = sociallogin.user
        user.set_unusable_password()
        if form:
            get_account_adapter().save_user(request, user, form)
        else:
            get_account_adapter().populate_username(request, user)
        sociallogin.save(request)
        Profile.objects.create(user=user).save()

        return user

    def populate_user(self, request, sociallogin, data):
        extra_data = sociallogin.account.extra_data

        name = data.get("name") or extra_data.get("name")
        email = data.get("email") or extra_data.get("email")
        handle = generate_handle()
        while User.objects.filter(handle=handle).exists():
            handle = generate_handle()

        user = sociallogin.user
        user.name = name or ""
        user_email(user, valid_email_or_none(email) or "")
        user.handle = handle
        return user
