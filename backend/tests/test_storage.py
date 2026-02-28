from uuid import uuid4

from docfabric.storage import FileStorage


class TestFileStorage:
    def test_save_and_read_original(self, tmp_path):
        storage = FileStorage(tmp_path)
        doc_id = uuid4()
        data = b"hello world"
        storage.save_original(doc_id, "test.txt", data)
        assert storage.read_original(doc_id, "test.txt") == data

    def test_original_path(self, tmp_path):
        storage = FileStorage(tmp_path)
        doc_id = uuid4()
        path = storage.original_path(doc_id, "test.txt")
        assert str(doc_id) in str(path)
        assert path.name == "test.txt"

    def test_save_and_read_markdown(self, tmp_path):
        storage = FileStorage(tmp_path)
        doc_id = uuid4()
        storage.save_markdown(doc_id, "# Title\n\nBody text")
        assert storage.read_markdown(doc_id) == "# Title\n\nBody text"

    def test_delete(self, tmp_path):
        storage = FileStorage(tmp_path)
        doc_id = uuid4()
        storage.save_original(doc_id, "test.txt", b"data")
        storage.save_markdown(doc_id, "# Markdown")

        storage.delete(doc_id)

        original_dir = tmp_path / "originals" / str(doc_id)
        md_path = tmp_path / "markdown" / f"{doc_id}.md"
        assert not original_dir.exists()
        assert not md_path.exists()

    def test_delete_nonexistent_is_safe(self, tmp_path):
        storage = FileStorage(tmp_path)
        storage.delete(uuid4())
