import pytest
import os
import zipfile
import tempfile
from unittest.mock import patch, MagicMock
from src.core.repo_ingestion import ingest_zip_file, ingest_github_repo, RepoIngestionError

def test_ingest_zip_file_success():
    # Create a temporary zip file
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
        zip_path = temp_zip.name

    try:
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('test.py', 'print("hello")')
            zf.writestr('folder/script.js', 'console.log("world");')
            zf.writestr('ignore.txt', 'should be ignored')

        contents = ingest_zip_file(zip_path)

        assert 'test.py' in contents
        assert contents['test.py'] == 'print("hello")'
        assert 'folder/script.js' in contents
        assert contents['folder/script.js'] == 'console.log("world");'
        assert 'ignore.txt' not in contents # We filter for code extensions
    finally:
        os.remove(zip_path)

def test_ingest_zip_file_invalid():
    # Create a non-zip file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"not a zip")
        file_path = temp_file.name

    try:
        with pytest.raises(RepoIngestionError, match="Invalid or corrupted zip file"):
            ingest_zip_file(file_path)
    finally:
        os.remove(file_path)

@patch('src.core.repo_ingestion.Github')
def test_ingest_github_repo_success(mock_github_class):
    mock_g = MagicMock()
    mock_github_class.return_value = mock_g

    mock_repo = MagicMock()
    mock_g.get_repo.return_value = mock_repo

    # Mock files
    file1 = MagicMock()
    file1.type = "file"
    file1.path = "main.py"
    file1.decoded_content = b'def main(): pass'

    file2 = MagicMock()
    file2.type = "file"
    file2.path = "app.ts"
    file2.decoded_content = b'const a = 1;'

    dir1 = MagicMock()
    dir1.type = "dir"
    dir1.path = "src"

    # Setup contents response
    # First call to get_contents("") returns dir1 and file1
    # Second call to get_contents("src") returns file2
    mock_repo.get_contents.side_effect = [
        [dir1, file1],
        [file2]
    ]

    contents = ingest_github_repo("https://github.com/owner/repo")

    assert "main.py" in contents
    assert contents["main.py"] == "def main(): pass"
    assert "app.ts" in contents
    assert contents["app.ts"] == "const a = 1;"

    mock_g.get_repo.assert_called_once_with("owner/repo")

def test_ingest_github_repo_invalid_url():
    with pytest.raises(RepoIngestionError, match="Invalid GitHub repository URL"):
        ingest_github_repo("not_a_url")
