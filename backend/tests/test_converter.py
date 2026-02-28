from unittest.mock import MagicMock, patch

from docfabric.conversion.converter import MarkdownConverter


class TestMarkdownConverter:
    def test_convert_calls_docling(self, tmp_path):
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf content")

        mock_result = MagicMock()
        mock_result.document.export_to_markdown.return_value = "# Converted"

        with patch(
            "docfabric.conversion.converter.DocumentConverter"
        ) as mock_dc_class:
            mock_dc_class.return_value.convert.return_value = mock_result
            converter = MarkdownConverter()
            markdown = converter.convert(test_file)

        assert markdown == "# Converted"
        mock_dc_class.return_value.convert.assert_called_once_with(str(test_file))

    def test_convert_propagates_error(self, tmp_path):
        test_file = tmp_path / "bad.pdf"
        test_file.write_bytes(b"bad content")

        with patch(
            "docfabric.conversion.converter.DocumentConverter"
        ) as mock_dc_class:
            mock_dc_class.return_value.convert.side_effect = RuntimeError("parse error")
            converter = MarkdownConverter()
            try:
                converter.convert(test_file)
                assert False, "Should have raised"
            except RuntimeError as e:
                assert "parse error" in str(e)
