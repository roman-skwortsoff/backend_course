from app.services.auth import AuthService


def test_decode_and_encode_access_token():
    data = {"user_id": 1}
    jwt_token = AuthService().create_access_token(data)

    assert jwt_token

    payload = AuthService().decode_token(jwt_token)

    assert payload
    assert payload["user_id"] == data["user_id"]
