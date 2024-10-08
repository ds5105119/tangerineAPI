from accounts.utils import *
from profiles.models import *

try:
    from allauth.account.adapter import DefaultAccountAdapter
    from allauth.account.utils import user_email
    from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
    from allauth.utils import valid_email_or_none
    from django.contrib.auth import get_user_model
    from django.core.exceptions import ValidationError
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")


User = get_user_model()


class AccountAdapter(DefaultAccountAdapter):
    """
    Custom Account Adapter
    """

    def clean_email(self, email):
        email = super().clean_email(email)
        if User.objects.filter(email=email).exists():
            raise ValidationError("이미 사용 중인 이메일 주소입니다.")
        return email

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """

        data = form.cleaned_data

        email = data.get("email")
        username = data.get("username")
        handle = generate_handle()
        while User.objects.filter(handle=handle).exists():
            handle = generate_handle()
        profile = Profile.objects.create()

        user.email = email
        user.username = username
        if "password1" in data:
            user.set_password(data["password1"])
        elif "password" in data:
            user.set_password(data["password"])
        else:
            user.set_unusable_password()
        self.populate_username(request, user)
        user.handle = handle
        user.profile = profile

        if commit:
            # Ability not to commit makes it easier to derive from
            # this adapter by adding
            user.save()
        return user


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom Social Account Adapter
    Override some methods to use the Profile model
    https://docs.allauth.org/en/latest/account/advanced.html
    """

    def pre_social_login(self, request, sociallogin):
        """
        같은 이메일로 가입된 일반 계정이 존재하는 경우 소셜 로그인 계정을 연동합니다.
        """
        email = sociallogin.account.extra_data.get("email", None)
        if email:
            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                sociallogin.connect(request, existing_user)

    def populate_user(self, request, sociallogin, data):
        """
        Custom User Model의 필드를 채웁니다.
        """
        extra_data = sociallogin.account.extra_data

        name = data.get("name") or extra_data.get("name")
        email = data.get("email") or extra_data.get("email")
        handle = generate_handle()
        while User.objects.filter(handle=handle).exists():
            handle = generate_handle()
        profile = Profile.objects.create()

        user = sociallogin.user
        user.username = name or ""
        user_email(user, valid_email_or_none(email) or "")
        user.handle = handle
        user.profile = profile
        return user
