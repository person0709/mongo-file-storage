from datetime import datetime
from io import FileIO
from pathlib import Path

import pytest
from bson import ObjectId
from fastapi import UploadFile

from db.database import Database
from db.model.file_meta import FileMeta
from db.respositories.file_repository import FileRepository


@pytest.mark.asyncio
async def test_add_file_text_non_duplicate(test_db: Database, text_file: Path):
    repo = FileRepository(test_db)
    # add file
    file_meta = await repo.add_file(
        storage_user_id="12345",
        file=UploadFile(filename=text_file.name, file=FileIO(text_file)),
    )
    # retrieve file and check metadata
    doc = await test_db.client["file_service"]["fs.files"].find_one({"_id": ObjectId(file_meta.id)})
    assert doc["filename"] == text_file.name
    assert doc["metadata"]["user_id"] == "12345"
    # check actual file content
    grid_out = await test_db.grid_client.open_download_stream(ObjectId(file_meta.id))
    with text_file.open("rb") as f:
        assert await grid_out.read() == f.read()


@pytest.mark.asyncio
async def test_add_file_text_duplicate(test_db: Database, text_file: Path):
    repo = FileRepository(test_db)
    # add file
    await repo.add_file(
        storage_user_id="12345",
        file=UploadFile(filename=text_file.name, file=FileIO(text_file)),
    )
    # try adding the same file again
    with pytest.raises(FileExistsError):
        await repo.add_file(
            storage_user_id="12345",
            file=UploadFile(filename=text_file.name, file=FileIO(text_file)),
        )


@pytest.mark.asyncio
async def test_add_file_image(test_db: Database, image_file: Path):
    repo = FileRepository(test_db)
    # add file
    file_meta = await repo.add_file(
        storage_user_id="12345",
        file=UploadFile(filename=image_file.name, file=FileIO(image_file)),
    )
    # retrieve file and check metadata
    doc = await test_db.client["file_service"]["fs.files"].find_one({"_id": ObjectId(file_meta.id)})
    assert doc["filename"] == image_file.name
    assert doc["metadata"]["user_id"] == "12345"
    # check actual file content
    grid_out = await test_db.grid_client.open_download_stream(ObjectId(file_meta.id))
    with image_file.open("rb") as f:
        assert await grid_out.read() == f.read()


@pytest.mark.asyncio
async def test_add_file_audio(test_db: Database, audio_file: Path):
    repo = FileRepository(test_db)
    # add file
    file_meta = await repo.add_file(
        storage_user_id="12345",
        file=UploadFile(filename=audio_file.name, file=FileIO(audio_file)),
    )
    # retrieve file and check metadata
    doc = await test_db.client["file_service"]["fs.files"].find_one({"_id": ObjectId(file_meta.id)})
    assert doc["filename"] == audio_file.name
    assert doc["metadata"]["user_id"] == "12345"
    # check actual file content
    grid_out = await test_db.grid_client.open_download_stream(ObjectId(file_meta.id))
    with audio_file.open("rb") as f:
        assert await grid_out.read() == f.read()


@pytest.mark.asyncio
async def test_download_file(test_db: Database, text_file: Path):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=text_file.name, source=f, metadata={"user_id": "12345"})
    file = await FileRepository(test_db).download_file(storage_user_id="12345", filename=text_file.name)
    with text_file.open("rb") as f:
        assert file == f.read()


@pytest.mark.asyncio
async def test_read_file_info(test_db: Database, text_file: Path):
    # add file
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=text_file.name, source=f, metadata={"user_id": "12345"})
    info = await FileRepository(test_db).read_file_info(storage_user_id="12345", filename=text_file.name)
    assert isinstance(info, FileMeta)
    assert info.filename == text_file.name
    assert info.user_id == "12345"
    assert info.uploaded_at.min == datetime.utcnow().min


@pytest.mark.asyncio
async def test_list_file_info_filename_desc(test_db: Database, text_file: Path, image_file: Path, audio_file: Path):
    # add 3 files with different names, sizes and types
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=text_file.name, source=f, metadata={"user_id": "12345"})
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=image_file.name, source=f, metadata={"user_id": "12345"})
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=audio_file.name, source=f, metadata={"user_id": "12345"})
    # test filename desc sort
    info_gen = FileRepository(test_db).list_files_info(
        storage_user_id="12345", offset=0, limit=3, sort_by="filename", desc=True
    )
    # convert async generator to a list
    info_list = [i async for i in info_gen]
    assert len(info_list) == 3
    # check descending order
    assert info_list[0].filename > info_list[1].filename
    assert info_list[1].filename > info_list[2].filename


@pytest.mark.asyncio
async def test_list_file_info_filename_asc(test_db: Database, text_file: Path, image_file: Path, audio_file: Path):
    # add 3 files with different names, sizes and types
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=text_file.name, source=f, metadata={"user_id": "12345"})
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=image_file.name, source=f, metadata={"user_id": "12345"})
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=audio_file.name, source=f, metadata={"user_id": "12345"})
    # test filename asc sort
    info_gen = FileRepository(test_db).list_files_info(
        storage_user_id="12345", offset=0, limit=3, sort_by="filename", desc=False
    )
    # convert async generator to a list
    info_list = [i async for i in info_gen]
    assert len(info_list) == 3
    # check ascending order
    assert info_list[2].filename > info_list[1].filename
    assert info_list[1].filename > info_list[0].filename


@pytest.mark.asyncio
async def test_list_file_info_date_desc(test_db: Database, text_file: Path, image_file: Path, audio_file: Path):
    # add 3 files with different names, sizes and types
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=text_file.name, source=f, metadata={"user_id": "12345"})
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=image_file.name, source=f, metadata={"user_id": "12345"})
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=audio_file.name, source=f, metadata={"user_id": "12345"})
    # test upload desc sort
    info_gen = FileRepository(test_db).list_files_info(
        storage_user_id="12345", offset=0, limit=3, sort_by="updateDate", desc=True
    )
    # convert async generator to a list
    info_list = [i async for i in info_gen]
    assert len(info_list) == 3
    # check descending order
    assert info_list[0].uploaded_at > info_list[1].uploaded_at
    assert info_list[1].uploaded_at > info_list[2].uploaded_at


@pytest.mark.asyncio
async def test_list_file_info_date_asc(test_db: Database, text_file: Path, image_file: Path, audio_file: Path):
    # add 3 files with different names, sizes and types
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=text_file.name, source=f, metadata={"user_id": "12345"})
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=image_file.name, source=f, metadata={"user_id": "12345"})
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=audio_file.name, source=f, metadata={"user_id": "12345"})
    # test upload asc sort
    info_gen = FileRepository(test_db).list_files_info(
        storage_user_id="12345", offset=0, limit=3, sort_by="updateDate", desc=False
    )
    # convert async generator to a list
    info_list = [i async for i in info_gen]
    assert len(info_list) == 3
    # check ascending order
    assert info_list[2].uploaded_at > info_list[1].uploaded_at
    assert info_list[1].uploaded_at > info_list[0].uploaded_at


@pytest.mark.asyncio
async def test_list_file_info_size_desc(test_db: Database, text_file: Path, image_file: Path, audio_file: Path):
    # add 3 files with different names, sizes and types
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=text_file.name, source=f, metadata={"user_id": "12345"})
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=image_file.name, source=f, metadata={"user_id": "12345"})
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=audio_file.name, source=f, metadata={"user_id": "12345"})
    # test file size desc sort
    info_gen = FileRepository(test_db).list_files_info(
        storage_user_id="12345", offset=0, limit=3, sort_by="length", desc=True
    )
    # convert async generator to a list
    info_list = [i async for i in info_gen]
    assert len(info_list) == 3
    # check descending order
    assert info_list[0].size > info_list[1].size
    assert info_list[1].size > info_list[2].size


@pytest.mark.asyncio
async def test_list_file_info_size_asc(test_db: Database, text_file: Path, image_file: Path, audio_file: Path):
    # add 3 files with different names, sizes and types
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=text_file.name, source=f, metadata={"user_id": "12345"})
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=image_file.name, source=f, metadata={"user_id": "12345"})
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=audio_file.name, source=f, metadata={"user_id": "12345"})
    # test file size asc sort
    info_gen = FileRepository(test_db).list_files_info(
        storage_user_id="12345", offset=0, limit=3, sort_by="length", desc=False
    )
    # convert async generator to a list
    info_list = [i async for i in info_gen]
    assert len(info_list) == 3
    # check ascending order
    assert info_list[2].size > info_list[1].size
    assert info_list[1].size > info_list[0].size


@pytest.mark.asyncio
async def test_list_file_info_offset(test_db: Database, text_file: Path, image_file: Path, audio_file: Path):
    # add 3 files with different names, sizes and types
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=text_file.name, source=f, metadata={"user_id": "12345"})
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=image_file.name, source=f, metadata={"user_id": "12345"})
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=audio_file.name, source=f, metadata={"user_id": "12345"})
    # set offset to 1 so the smallest file(text file) gets skipped
    info_gen = FileRepository(test_db).list_files_info(
        storage_user_id="12345", offset=1, limit=3, sort_by="length", desc=False
    )
    # convert async generator to a list
    info_list = [i async for i in info_gen]
    assert len(info_list) == 2
    # check text file is skipped
    assert text_file.name not in [info.filename for info in info_list]


@pytest.mark.asyncio
async def test_list_file_info_limit(test_db: Database, text_file: Path, image_file: Path, audio_file: Path):
    # add 3 files with different names, sizes and types
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=text_file.name, source=f, metadata={"user_id": "12345"})
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=image_file.name, source=f, metadata={"user_id": "12345"})
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=audio_file.name, source=f, metadata={"user_id": "12345"})
    # set limit to 2 so the biggest file(audio file) is not included
    info_gen = FileRepository(test_db).list_files_info(
        storage_user_id="12345", offset=0, limit=2, sort_by="length", desc=False
    )
    # convert async generator to a list
    info_list = [i async for i in info_gen]
    assert len(info_list) == 2
    # check audio file is not included
    assert audio_file.name not in [info.filename for info in info_list]


@pytest.mark.asyncio
async def test_search_by_regex(test_db: Database, text_file: Path, image_file: Path, audio_file: Path):
    # add 3 files with different names, sizes and types
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename="test_file1.txt", source=f, metadata={"user_id": "12345"})
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename="image_file.jpg", source=f, metadata={"user_id": "12345"})
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename="aud_file1.wav", source=f, metadata={"user_id": "12345"})
    # get files that have a digit in the name
    info_gen = FileRepository(test_db).search_files_by_regex(storage_user_id="12345", limit=3, pattern="\d")
    # convert async generator to a list
    info_list = [i async for i in info_gen]
    # there are 2 files with a digit in the name
    assert len(info_list) == 2


@pytest.mark.asyncio
async def test_list_file_info_empty(test_db: Database, text_file: Path, image_file: Path, audio_file: Path):
    info_gen = FileRepository(test_db).list_files_info(
        storage_user_id="12345", offset=0, limit=3, sort_by="length", desc=False
    )
    # convert async generator to a list
    info_list = [i async for i in info_gen]
    assert len(info_list) == 0


@pytest.mark.asyncio
async def test_get_files_count(test_db: Database, text_file: Path, image_file: Path, audio_file: Path):
    # add 3 files with different names, sizes and types
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename="test_file1.txt", source=f, metadata={"user_id": "12345"})
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename="image_file2.jpg", source=f, metadata={"user_id": "12345"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename="aud_file1.wav", source=f, metadata={"user_id": "12345"})
    count = await FileRepository(test_db).get_files_count(storage_user_id="12345")
    assert count == 3


@pytest.mark.asyncio
async def test_delete_file(test_db: Database, text_file: Path):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename=text_file.name, source=f, metadata={"user_id": "12345"})
    # there should be an entry in the collection
    assert test_db.client["file_service"]["fs.files"].find().to_list(10)
    await FileRepository(test_db).delete_file(storage_user_id="12345", filename=text_file.name)
    # there shouldn't be any entry in the collection after the delete
    assert not await test_db.client["file_service"]["fs.files"].find().to_list(10)


@pytest.mark.asyncio
async def test_delete_non_existent_file(test_db: Database, text_file: Path):
    result = await FileRepository(test_db).delete_file(storage_user_id="12345", filename=text_file.name)
    assert result is False


@pytest.mark.asyncio
async def test_get_storage_usage(test_db: Database, text_file: Path, audio_file: Path, image_file: Path):
    with text_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename="test_file1.txt", source=f, metadata={"user_id": "12345"})
    with image_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(
            filename="image_file2.jpg", source=f, metadata={"user_id": "12345"}
        )
    with audio_file.open("rb") as f:
        await test_db.grid_client.upload_from_stream(filename="aud_file1.wav", source=f, metadata={"user_id": "12345"})
    result = await FileRepository(test_db).get_storage_usage("12345")
    size_sum = text_file.stat().st_size + audio_file.stat().st_size + image_file.stat().st_size
    assert result == size_sum
