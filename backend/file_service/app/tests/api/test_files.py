"""
Test all endpoints against common use cases.
"""
from datetime import datetime
from pathlib import Path

import pytest
from httpx import AsyncClient
from jose import jwt
from starlette import status

from api.models.jwt_payload import JWTPayload
from api.models.role import Role
from config import settings
from tests.db.mock_database import MockDatabase


@pytest.mark.asyncio
async def test_upload_fail_auth(
    test_client: AsyncClient, test_db: MockDatabase, text_file: Path
):
    payload = JWTPayload(
        # generate jwt with an expired date
        sub="uploader_id",
        role=Role.UPLOADER,
        exp=datetime(2000, 1, 1),
        username="you",
        email="shall@not.pass",
    )
    files = {"file": text_file.open(mode="rb")}
    response = await test_client.post(
        "/api/files/upload",
        files=files,
        headers={
            "Authorization": f"Bearer {jwt.encode(payload.dict(), key=settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)}"
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_upload_as_admin(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    admin_token_header: str,
):
    files = {"file": text_file.open(mode="rb")}
    response = await test_client.post(
        "/api/files/upload",
        files=files,
        headers=admin_token_header,
    )
    # check there is an entry with the uploaded filename
    assert await test_db.client["file_service"]["fs.files"].find_one(
        {"filename": response.json()["filename"]}
    )


@pytest.mark.asyncio
async def test_upload_image_as_admin(
    test_client: AsyncClient,
    test_db: MockDatabase,
    image_file: Path,
    admin_token_header: str,
):
    files = {"file": image_file.open(mode="rb")}
    response = await test_client.post(
        "/api/files/upload",
        files=files,
        headers=admin_token_header,
    )
    # check there is an entry with the uploaded filename
    assert await test_db.client["file_service"]["fs.files"].find_one(
        {"filename": response.json()["filename"]}
    )


@pytest.mark.asyncio
async def test_upload_to_others_storage_as_admin(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    admin_token_header: str,
):
    files = {"file": text_file.open(mode="rb")}
    await test_client.post(
        "/api/files/upload",
        data={"user_id": "some_id"},
        files=files,
        headers=admin_token_header,
    )
    # check there is an entry with the uploaded filename
    assert await test_db.client["file_service"]["fs.files"].find_one(
        {"filename": text_file.name, "metadata": {"user_id": "some_id"}}
    )


@pytest.mark.asyncio
async def test_upload_file_limit(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    admin_token_header: str,
    monkeypatch,
):
    monkeypatch.setattr(settings, "FILE_SIZE_LIMIT", 100)
    files = {"file": text_file.open(mode="rb")}
    response = await test_client.post(
        "/api/files/upload",
        data={"user_id": "some_id"},
        files=files,
        headers=admin_token_header,
    )
    assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE


@pytest.mark.asyncio
async def test_upload_duplicate_filename(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    admin_token_header: str,
):
    files = {"file": text_file.open(mode="rb")}
    response = await test_client.post(
        "/api/files/upload",
        files=files,
        headers=admin_token_header,
    )
    # check there is an entry with the uploaded filename
    assert await test_db.client["file_service"]["fs.files"].find_one(
        {"filename": response.json()["filename"]}
    )
    # upload the same file again
    files = {"file": text_file.open(mode="rb")}
    response = await test_client.post(
        "/api/files/upload",
        files=files,
        headers=admin_token_header,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_upload_disallowed_extension(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    admin_token_header: str,
):
    # send file with an unknown extension
    files = {"file": ("illegal.ext", text_file.open(mode="rb"), None)}
    response = await test_client.post(
        "/api/files/upload",
        files=files,
        data={"user_id": "some_id"},
        headers=admin_token_header,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_upload_as_uploader(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    uploader_token_header: str,
):
    files = {"file": text_file.open(mode="rb")}
    response = await test_client.post(
        "/api/files/upload",
        files=files,
        headers=uploader_token_header,
    )
    # check there is an entry with the uploaded filename
    assert await test_db.client["file_service"]["fs.files"].find_one(
        {"filename": response.json()["filename"]}
    )


@pytest.mark.asyncio
async def test_upload_to_others_storage_as_uploader(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    uploader_token_header: str,
):
    files = {"file": text_file.open(mode="rb")}
    response = await test_client.post(
        "/api/files/upload",
        data={"user_id": "some_id"},
        files=files,
        headers=uploader_token_header,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_upload_as_viewer(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    viewer_token_header: str,
):
    files = {"file": text_file.open(mode="rb")}
    response = await test_client.post(
        "/api/files/upload",
        files=files,
        headers=viewer_token_header,
    )
    # viewer should not be able to upload
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_download_as_admin(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    admin_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename="text.txt", source=f, metadata={"user_id": "admin_id"}
        )
    response = await test_client.get(
        "/api/files/download",
        params={"filename": "text.txt"},
        headers=admin_token_header,
    )
    # check downloaded content matches
    with text_file.open("rb") as f:
        assert f.read() == response.content


@pytest.mark.asyncio
async def test_download_from_others_storage_as_admin(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    admin_token_header: str,
):
    # upload a file to some other user's storage
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename="text.txt", source=f, metadata={"user_id": "some_id"}
        )
    response = await test_client.get(
        "/api/files/download",
        params={"filename": "text.txt", "user_id": "some_id"},
        headers=admin_token_header,
    )
    # check downloaded content matches
    with text_file.open("rb") as f:
        assert f.read() == response.content


@pytest.mark.asyncio
async def test_download_as_uploader(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    uploader_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename="text.txt", source=f, metadata={"user_id": "uploader_id"}
        )
    response = await test_client.get(
        "/api/files/download",
        params={"filename": "text.txt"},
        headers=uploader_token_header,
    )
    # check downloaded content matches
    with text_file.open("rb") as f:
        assert f.read() == response.content


@pytest.mark.asyncio
async def test_download_from_others_storage_as_uploader(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    uploader_token_header: str,
):
    # upload a file to some other user's storage
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename="text.txt", source=f, metadata={"user_id": "some_id"}
        )
    response = await test_client.get(
        "/api/files/download",
        params={"filename": "text.txt", "user_id": "some_id"},
        headers=uploader_token_header,
    )
    # should not be able to download from other user's storage
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_download_as_viewer(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    viewer_token_header: str,
):
    response = await test_client.get(
        "/api/files/download",
        params={"filename": "text.txt"},
        headers=viewer_token_header,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_download_non_existent(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    uploader_token_header: str,
):
    response = await test_client.get(
        "/api/files/download",
        params={"filename": "text.txt"},
        headers=uploader_token_header,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_read_file_info_as_admin(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    admin_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename="text.txt", source=f, metadata={"user_id": "admin_id"}
        )
    response = await test_client.get(
        "/api/files", params={"filename": "text.txt"}, headers=admin_token_header
    )
    assert "filename" in response.json()
    assert "uploaded_at" in response.json()
    assert "size" in response.json()
    assert "md5" in response.json()
    assert "user_id" not in response.json()


@pytest.mark.asyncio
async def test_read_file_info_from_others_storage_as_admin(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    admin_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename="text.txt", source=f, metadata={"user_id": "some_id"}
        )
    response = await test_client.get(
        "/api/files",
        params={"filename": "text.txt", "user_id": "some_id"},
        headers=admin_token_header,
    )
    assert "filename" in response.json()
    assert "uploaded_at" in response.json()
    assert "size" in response.json()
    assert "md5" in response.json()
    assert "user_id" not in response.json()


@pytest.mark.asyncio
async def test_read_file_info_as_uploader(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    uploader_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename="text.txt", source=f, metadata={"user_id": "uploader_id"}
        )
    response = await test_client.get(
        "/api/files", params={"filename": "text.txt"}, headers=uploader_token_header
    )
    assert "filename" in response.json()
    assert "uploaded_at" in response.json()
    assert "size" in response.json()
    assert "md5" in response.json()
    assert "user_id" not in response.json()


@pytest.mark.asyncio
async def test_read_file_info_from_others_storage_as_uploader(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    uploader_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename="text.txt", source=f, metadata={"user_id": "some_id"}
        )
    response = await test_client.get(
        "/api/files",
        params={"filename": "text.txt", "user_id": "some_id"},
        headers=uploader_token_header,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_read_file_info_as_viewer(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    viewer_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename="text.txt", source=f, metadata={"user_id": "viewer_id"}
        )
    response = await test_client.get(
        "/api/files", params={"filename": "text.txt"}, headers=viewer_token_header
    )
    assert "filename" in response.json()
    assert "uploaded_at" in response.json()
    assert "size" in response.json()
    assert "md5" in response.json()
    assert "user_id" not in response.json()


@pytest.mark.asyncio
async def test_read_file_info_from_others_storage_as_viewer(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    viewer_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename="text.txt", source=f, metadata={"user_id": "some_id"}
        )
    response = await test_client.get(
        "/api/files",
        params={"filename": "text.txt", "user_id": "some_id"},
        headers=viewer_token_header,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_read_non_existent_file_info(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    viewer_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename="text.txt", source=f, metadata={"user_id": "some_id"}
        )
    response = await test_client.get(
        "/api/files", params={"filename": "text.txt"}, headers=viewer_token_header
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_read_file_info_list_as_admin(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    admin_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "admin_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "admin_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "admin_id"}
        )
    response = await test_client.get(
        "/api/files/list/", params={}, headers=admin_token_header
    )
    assert len(response.json()["files"]) == 3


@pytest.mark.asyncio
async def test_read_file_info_list_from_others_storage_as_admin(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    admin_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "some_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "some_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "some_other_id"}
        )
    response = await test_client.get(
        "/api/files/list", params={"user_id": "some_id"}, headers=admin_token_header
    )
    assert len(response.json()["files"]) == 2


@pytest.mark.asyncio
async def test_read_file_info_list_as_uploader(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    uploader_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "uploader_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "uploader_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "uploader_id"}
        )
    response = await test_client.get(
        "/api/files/list", params={}, headers=uploader_token_header
    )
    assert len(response.json()["files"]) == 3


@pytest.mark.asyncio
async def test_read_file_info_list_from_others_storage_as_uploader(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    uploader_token_header: str,
):
    response = await test_client.get(
        "/api/files/list", params={"user_id": "some_id"}, headers=uploader_token_header
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_read_file_info_list_as_viewer(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    viewer_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "viewer_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "viewer_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "viewer_id"}
        )
    response = await test_client.get(
        "/api/files/list", params={}, headers=viewer_token_header
    )
    assert len(response.json()["files"]) == 3


@pytest.mark.asyncio
async def test_read_file_info_list_from_others_storage_as_viewer(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    viewer_token_header: str,
):
    response = await test_client.get(
        "/api/files/list", params={"user_id": "some_id"}, headers=viewer_token_header
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_list_file_info_from_others_storage_as_viewer(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    viewer_token_header: str,
):
    response = await test_client.get(
        "/api/files/list", params={"user_id": "some_id"}, headers=viewer_token_header
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_read_file_info_list_offset_limit(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    viewer_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "viewer_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "viewer_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "viewer_id"}
        )
    response = await test_client.get(
        "/api/files/list", params={"offset": 1, "limit": 2}, headers=viewer_token_header
    )
    assert len(response.json()["files"]) == 2


@pytest.mark.asyncio
async def test_list_file_info_sort_by_conversion(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    viewer_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "viewer_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "viewer_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "viewer_id"}
        )
    response = await test_client.get(
        "/api/files/list",
        params={"sort_by": "size", "desc": "True"},
        headers=viewer_token_header,
    )
    assert len(response.json()["files"]) == 3
    assert response.json()["files"][0]["size"] > response.json()["files"][1]["size"]
    assert response.json()["files"][1]["size"] > response.json()["files"][2]["size"]


@pytest.mark.asyncio
async def test_search_file_info_as_admin(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    admin_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "admin_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "admin_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "admin_id"}
        )
    response = await test_client.get(
        "/api/files/search", params={"pattern": "text"}, headers=admin_token_header
    )
    assert len(response.json()["files"]) == 1


@pytest.mark.asyncio
async def test_search_file_info_from_others_storage_as_admin(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    admin_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "some_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "some_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "some_other_id"}
        )
    response = await test_client.get(
        "/api/files/search",
        params={"pattern": "text", "user_id": "some_id"},
        headers=admin_token_header,
    )
    assert len(response.json()["files"]) == 1


@pytest.mark.asyncio
async def test_search_file_info_as_uploader(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    uploader_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "uploader_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "uploader_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "uploader_id"}
        )
    response = await test_client.get(
        "/api/files/search", params={"pattern": "text"}, headers=uploader_token_header
    )
    assert len(response.json()["files"]) == 1


@pytest.mark.asyncio
async def test_list_file_info_from_others_storage_as_uploader(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    uploader_token_header: str,
):
    response = await test_client.get(
        "/api/files/list", params={"user_id": "some_id"}, headers=uploader_token_header
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_search_file_info_as_viewer(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    viewer_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "viewer_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "viewer_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "viewer_id"}
        )
    response = await test_client.get(
        "/api/files/search", params={"pattern": "text"}, headers=viewer_token_header
    )
    assert len(response.json()["files"]) == 1


@pytest.mark.asyncio
async def test_search_file_from_others_storage_as_viewer(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    viewer_token_header: str,
):
    response = await test_client.get(
        "/api/files/search/",
        params={"user_id": "some_id", "pattern": "pattern"},
        headers=viewer_token_header,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_file_as_admin(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    admin_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "admin_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "admin_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "admin_id"}
        )
    response = await test_client.delete(
        "/api/files",
        params={"filename": image_file.name, "user_id": "admin_id"},
        headers=admin_token_header,
    )
    assert response.json()["filename"] == image_file.name
    # confirm it's deleted
    assert not await test_db.client["file_service"]["fs.files"].find_one(
        {"filename": image_file.name}
    )


@pytest.mark.asyncio
async def test_delete_file_from_others_storage_as_admin(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    admin_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "some_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "some_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "some_other_id"}
        )
    response = await test_client.delete(
        "/api/files",
        params={"filename": image_file.name, "user_id": "some_id"},
        headers=admin_token_header,
    )
    assert response.json()["filename"] == image_file.name
    # confirm it's deleted
    assert not await test_db.client["file_service"]["fs.files"].find_one(
        {"filename": image_file.name}
    )


@pytest.mark.asyncio
async def test_delete_non_existent_file(
    test_client: AsyncClient, test_db: MockDatabase, admin_token_header: str
):
    response = await test_client.delete(
        "/api/files",
        params={"filename": "non-existent-file", "user_id": "admin_id"},
        headers=admin_token_header,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_file_as_uploader(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    uploader_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "uploader_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "uploader_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "uploader_id"}
        )
    response = await test_client.delete(
        "/api/files",
        params={"filename": audio_file.name},
        headers=uploader_token_header,
    )
    assert response.json()["filename"] == audio_file.name
    # confirm it's deleted
    assert not await test_db.client["file_service"]["fs.files"].find_one(
        {"filename": audio_file.name}
    )


@pytest.mark.asyncio
async def test_delete_file_from_others_storage_as_uploader(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    uploader_token_header: str,
):
    response = await test_client.delete(
        "/api/files",
        params={"filename": "some_file", "user_id": "some_id"},
        headers=uploader_token_header,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_file_as_viewer(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    viewer_token_header: str,
):
    response = await test_client.delete(
        "/api/files", params={"filename": "some_file"}, headers=viewer_token_header
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_file_from_others_storage_as_viewer(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    viewer_token_header: str,
):
    response = await test_client.delete(
        "/api/files",
        params={"filename": "some_file", "user_id": "some_id"},
        headers=viewer_token_header,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_count_file_as_admin(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    admin_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "admin_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "admin_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "admin_id"}
        )
    response = await test_client.get(
        "/api/files/count", params={}, headers=admin_token_header
    )
    assert response.json()["count"] == 3


@pytest.mark.asyncio
async def test_count_file_from_others_storage_as_admin(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    admin_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "some_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "some_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "some_other_id"}
        )
    response = await test_client.get(
        "/api/files/count", params={"user_id": "some_id"}, headers=admin_token_header
    )
    assert response.json()["count"] == 2


@pytest.mark.asyncio
async def test_count_file_as_uploader(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    uploader_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "uploader_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "uploader_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "uploader_id"}
        )
    response = await test_client.get(
        "/api/files/count", params={}, headers=uploader_token_header
    )
    assert response.json()["count"] == 3


@pytest.mark.asyncio
async def test_count_file_from_others_storage_as_uploader(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    uploader_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "some_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "some_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "some_other_id"}
        )
    response = await test_client.get(
        "/api/files/count", params={"user_id": "some_id"}, headers=uploader_token_header
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_count_file_as_viewer(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    viewer_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "viewer_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "viewer_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "viewer_id"}
        )
    response = await test_client.get(
        "/api/files/count", params={}, headers=viewer_token_header
    )
    assert response.json()["count"] == 3


@pytest.mark.asyncio
async def test_count_file_from_others_storage_as_viewer(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    viewer_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "some_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "some_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "some_other_id"}
        )
    response = await test_client.get(
        "/api/files/count", params={"user_id": "some_id"}, headers=viewer_token_header
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_usage_as_admin(
    test_client: AsyncClient,
    test_db: MockDatabase,
    text_file: Path,
    image_file: Path,
    audio_file: Path,
    admin_token_header: str,
):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=text_file.name, source=f, metadata={"user_id": "some_id"}
        )
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=image_file.name, source=f, metadata={"user_id": "some_id"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename=audio_file.name, source=f, metadata={"user_id": "some_other_id"}
        )
    response = await test_client.get(
        "/api/files/usage", params={"user_id": "some_id"}, headers=admin_token_header
    )
    assert (
        response.json()["storage_used"]
        == text_file.stat().st_size + image_file.stat().st_size
    )
