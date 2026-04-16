import asyncio
from io import BytesIO
import os
from types import SimpleNamespace

from starlette.datastructures import Headers
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.services.storage import S3StorageService


class FakeS3Client:
    def __init__(self) -> None:
        self.put_object_calls: list[dict[str, object]] = []

    def put_object(self, **kwargs: object) -> None:
        self.put_object_calls.append(kwargs)


def test_s3_storage_service_uploads_object(monkeypatch) -> None:
    fake_client = FakeS3Client()

    settings = SimpleNamespace(
        s3_bucket_name="foodsnap-test-bucket",
        s3_upload_prefix="test-prefix",
        aws_region="eu-central-1",
    )
    monkeypatch.setattr("app.services.storage.get_settings", lambda: settings)

    def fake_boto3_client(service_name: str, region_name: str):
        assert service_name == "s3"
        assert region_name == "eu-central-1"
        return fake_client

    monkeypatch.setattr("app.services.storage.boto3.client", fake_boto3_client)

    upload = StarletteUploadFile(
        file=BytesIO(b"fake-image-bytes"),
        filename="pizza-lunch.jpg",
        headers=Headers({"content-type": "image/jpeg"}),
    )

    image_url = asyncio.run(S3StorageService().save_upload("meal_test", upload))

    assert image_url.startswith("s3://foodsnap-test-bucket/test-prefix/")
    assert image_url.endswith(".jpg")
    assert len(fake_client.put_object_calls) == 1

    call = fake_client.put_object_calls[0]
    assert call["Bucket"] == "foodsnap-test-bucket"
    assert str(call["Key"]).startswith("test-prefix/")
    assert call["Body"] == b"fake-image-bytes"
    assert call["ContentType"] == "image/jpeg"
