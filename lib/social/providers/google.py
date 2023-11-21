from typing import Optional, Tuple

from lib.social.social import SocialProvider
from common.dataclassform import SocialProfile


class Google(SocialProvider):
    """소셜 로그인
    doc:
    https://developers.google.com/identity/sign-in/web/sign-in
    클래스 메서드만 사용하며 인스턴스를 생성하지 않는다.
    """
    provider_name = "google"
    meta_data_url = "https://accounts.google.com/.well-known/openid-configuration"

    @classmethod
    def register(cls, oauth_instance, client_id, client_secret):
        oauth_instance.register(
            name=cls.provider_name,
            access_token_url="https://accounts.google.com/o/oauth2/token",
            access_token_params=None,
            authorize_url="https://accounts.google.com/o/oauth2/auth",
            authorize_params=None,
            api_base_url="https://www.googleapis.com",
            server_metadata_url=cls.meta_data_url,
            client_kwargs={
                'response_type': 'code',
                'token_endpoint_auth_method': 'client_secret_post',
                "scope": "email profile"
            },
        )

        oauth_instance.__getattr__(cls.provider_name).client_id = client_id
        oauth_instance.__getattr__(cls.provider_name).client_secret = client_secret

    @classmethod
    async def fetch_profile_data(cls, oauth_instance, auth_token) -> Optional[object]:
        """
        소셜 로그인 후 프로필 정보를 가져온다.
        Args:
            oauth_instance (OAuth): OAuth 인증 객체
            auth_token (Dict): 소셜 서비스 토큰
        Returns:
            SocialProfile
        Raises:
            HTTPException: HTTP status code 200 아닐 때 발생
            ValueError: 소셜 로그인 실패 시 발생
        """
        response = await oauth_instance.__getattr__(cls.provider_name).get(
            'https://www.googleapis.com/oauth2/v3/userinfo', token=auth_token)
        # raise http status code 200 아닐 때 발생
        response.raise_for_status()
        result = response.json()
        if (result.get("sub", None) is None and
                result.get("id", None) is None and
                result.get("email", None) is None):
            raise ValueError(result)

        return result

    @classmethod
    def convert_gnu_profile_data(cls, response) -> Tuple[str, SocialProfile]:
        """
        그누보드 MemberSocialProfiles 에서 사용하는 SocialProfile 형식으로 변환
        Args:
            response: 소셜 제공자에서 받은 프로필 정보
        """
        email = response.get("email", "")
        if response.get("sub", "") == "":
            identifier = response.get("id", "")
        else:
            identifier = response.get("sub", "")

        socialprofile = SocialProfile(
            mb_id=response.get("sub", ""),
            provider=cls.provider_name,
            identifier=identifier,
            profile_url=response.get("avatar", ""),
            photourl=response.get("avatar", ""),
            displayname=response.get("nickname", ""),
            disciption=""
        )

        return email, socialprofile
