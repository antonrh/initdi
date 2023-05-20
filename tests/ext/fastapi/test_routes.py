from unittest import mock

from starlette.testclient import TestClient

import pyxdi

from tests.ext.fixtures import TEST_EMAIL, Mail, MailService, User, UserService


def test_send_mail(client: TestClient) -> None:
    message = "test"

    response = client.post("/send-mail", json={"message": message})

    assert response.status_code == 200
    assert response.json() == {
        "email": TEST_EMAIL,
        "message": message,
    }


def test_send_mail_lazy(client: TestClient, di: pyxdi.PyxDI) -> None:
    message = "lazy"

    mail_service_init = mock.Mock()

    @di.provider(scope="singleton", override=True)
    def mail_service() -> MailService:
        mail_service_init()
        return mock.MagicMock(spec=MailService)

    response = client.post("/send-mail", json={"message": message})

    assert response.status_code == 200
    assert response.json() == {
        "email": TEST_EMAIL,
        "message": message,
    }

    mail_service_init.assert_not_called()


def test_send_mail_mock_mail_service(client: TestClient, di: pyxdi.PyxDI) -> None:
    mail = Mail(email="mock@mail.com", message="mock")

    mail_service_mock = mock.MagicMock(spec=MailService)
    mail_service_mock.send_mail.return_value = mail

    with di.override(MailService, instance=mail_service_mock):
        response = client.post("/send-mail", json={"message": mail.message})

    assert response.status_code == 200
    assert response.json() == {
        "email": mail.email,
        "message": mail.message,
    }


def test_send_mail_mock_user_service(client: TestClient, di: pyxdi.PyxDI) -> None:
    user = User(id=100, email="mock@mail.com")
    message = "hello"

    user_service_mock = mock.MagicMock(spec=UserService)
    user_service_mock.get_user.return_value = user

    with di.override(UserService, instance=user_service_mock):
        response = client.post("/send-mail", json={"message": message})

    assert response.status_code == 200
    assert response.json() == {
        "email": user.email,
        "message": message,
    }
