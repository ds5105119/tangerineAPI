from profiles.serializers import *

try:
    from dj_rest_auth.registration.serializers import *
    from dj_rest_auth.registration.serializers import SocialLoginSerializer
    from dj_rest_auth.serializers import LoginSerializer as DefaultLoginSerializer
    from django.contrib.auth import get_user_model
    from django.utils.translation import gettext_lazy as _
    from rest_framework import serializers
except ImportError:
    raise ImportError("django, django-rest-framework, dj-rest-accounts needs to be added to INSTALLED_APPS.")


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model
    FOR INTERNAL USE ONLY
    """

    profile = ProfileSelfSerializer()

    class Meta:
        model = User
        fields = (
            "handle",
            "username",
            "email",
            "profile",
            "created_at",
            "updated_at",
            "is_staff",
            "is_public",
            "follows_count",
            "followers_count",
        )


class WriteableUserSelfSerializer(serializers.ModelSerializer):
    """
    유저 자신이 수정 가능한 유저 모델의 필드를 정의합니다.
    """

    profile = ProfileSelfSerializer()

    class Meta:
        model = User
        fields = (
            "handle",
            "username",
            "profile",
        )

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)

        profile_data = validated_data.pop("profile")
        profile_serializer = ProfileSelfSerializer(instance.profile, data=profile_data, partial=True)
        if profile_serializer.is_valid(raise_exception=True):
            profile_serializer.save()

        return instance


class HandleOnlySerializer(serializers.ModelSerializer):
    """
    외부에서 유저의 handle로만 접근하는 것을 도와주는 시리얼라이저입니다.
    """

    class Meta:
        model = User
        fields = ("handle",)


class ReadOnlyUserSelfSerializer(serializers.ModelSerializer):
    """
    읽을 수 있는 유저 자신의 유저 모델 필드를 정의합니다.
    """

    profile = ProfileSelfSerializer()

    class Meta:
        model = User
        fields = (
            "handle",
            "username",
            "email",
            "profile",
            "created_at",
            "updated_at",
            "is_staff",
            "is_public",
            "follows_count",
            "followers_count",
        )


class ReadOnlyUserInternalSerializer(serializers.ModelSerializer):
    """
    읽을 수 있는 다른 유저들의 유저 모델 필드를 정의합니다.
    """

    profile = ProfileExternalSerializer()
    is_following = serializers.BooleanField()
    is_follower = serializers.BooleanField()

    class Meta:
        model = User
        fields = (
            "handle",
            "username",
            "profile",
            "created_at",
            "updated_at",
            "is_public",
            "follows_count",
            "followers_count",
            "is_following",
            "is_follower",
        )


class ReadOnlyUserExternalSerializer(serializers.ModelSerializer):
    """
    읽을 수 있는 다른 유저들의 유저 모델 필드를 정의합니다.
    """

    profile = ProfileExternalSerializer()

    class Meta:
        model = User
        fields = (
            "handle",
            "username",
            "profile",
            "created_at",
            "updated_at",
            "is_public",
            "follows_count",
            "followers_count",
        )


class LoginSerializer(DefaultLoginSerializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(style={"input_type": "password"})


class CustomSocialLoginSerializer(SocialLoginSerializer):
    """
    Since dj-rest-auth currently only supports allauth <= 0.61.1,
    dj_rest_auth.registration.serializers.SocialLoginSerializer.validate method is not compatible
    with get_scope of adapter in allauth version 0.62.0 and higher.
    an override has been applied to use the latest allauth.
    https://github.com/iMerica/dj-rest-auth/issues/639
    """

    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except TypeError:
            return self.custom_validate(attrs)

    def custom_validate(self, attrs):
        view = self.context.get("view")
        request = self._get_request()

        if not view:
            raise serializers.ValidationError(
                _("View is not defined, pass it as a context variable"),
            )

        adapter_class = getattr(view, "adapter_class", None)
        if not adapter_class:
            raise serializers.ValidationError(_("Define adapter_class in view"))

        adapter = adapter_class(request)
        app = adapter.get_provider().app

        # More info on code vs access_token
        # http://stackoverflow.com/questions/8666316/facebook-oauth-2-0-code-and-token

        access_token = attrs.get("access_token")
        code = attrs.get("code")
        # Case 1: We received the access_token
        if access_token:
            tokens_to_parse = {"access_token": access_token}
            token = access_token
            # For sign in with apple
            id_token = attrs.get("id_token")
            if id_token:
                tokens_to_parse["id_token"] = id_token

        # Case 2: We received the authorization code
        elif code:
            self.set_callback_url(view=view, adapter_class=adapter_class)
            self.client_class = getattr(view, "client_class", None)

            if not self.client_class:
                raise serializers.ValidationError(
                    _("Define client_class in view"),
                )

            client = self.client_class(
                request,
                app.client_id,
                app.secret,
                adapter.access_token_method,
                adapter.access_token_url,
                self.callback_url,
                scope_delimiter=adapter.scope_delimiter,
                headers=adapter.headers,
                basic_auth=adapter.basic_auth,
            )
            try:
                token = client.get_access_token(code)
            except OAuth2Error as ex:
                raise serializers.ValidationError(
                    _(f"Failed to exchange code for access token, received: {ex}")
                ) from ex
            access_token = token["access_token"]
            tokens_to_parse = {"access_token": access_token}

            # If available we add additional data to the dictionary
            for key in ["refresh_token", "id_token", adapter.expires_in_key]:
                if key in token:
                    tokens_to_parse[key] = token[key]
        else:
            raise serializers.ValidationError(
                _("Incorrect input. access_token or code is required."),
            )

        social_token = adapter.parse_token(tokens_to_parse)
        social_token.app = app

        try:
            if adapter.provider_id == "google" and not code:
                login = self.get_social_login(adapter, app, social_token, response={"id_token": id_token})
            else:
                login = self.get_social_login(adapter, app, social_token, token)
            ret = complete_social_login(request, login)
        except HTTPError:
            raise serializers.ValidationError(_("Incorrect value"))

        if isinstance(ret, HttpResponseBadRequest):
            raise serializers.ValidationError(ret.content)

        if not login.is_existing:
            # We have an account already signed up in a different flow
            # with the same email address: raise an exception.
            # This needs to be handled in the frontend. We can not just
            # link up the accounts due to security constraints
            if allauth_account_settings.UNIQUE_EMAIL:
                # Do we have an account already with this email address?
                account_exists = (
                    get_user_model()
                    .objects.filter(
                        email=login.user.email,
                    )
                    .exists()
                )
                if account_exists:
                    raise serializers.ValidationError(
                        _("User is already registered with this e-mail address."),
                    )

            login.lookup()
            try:
                login.save(request, connect=True)
            except IntegrityError as ex:
                raise serializers.ValidationError(
                    _("User is already registered with this e-mail address."),
                ) from ex
            self.post_signup(login, attrs)

        attrs["user"] = login.account.user

        return attrs
