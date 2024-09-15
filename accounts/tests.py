import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_google_login(client):
    """
    구글 로그인 테스트

    과정:
        응답이 400여부인지 확인, 아닌 경우 실패
        응답에 "non_field_errors" key가 있는지 확인, 없는 경우 실패
    """

    fake_code = "fake_google_auth_code"

    url = reverse("google_login")
    response = client.post(url, {"code": fake_code})

    assert response.status_code == 400
    assert response.data["non_field_errors"]
