import os
import zipfile
import tempfile
from typing import Dict, Any, List
from github import Github, Auth
import requests

class RepoIngestionError(Exception):
    """Exception raised for errors in repository ingestion."""
    pass

def ingest_zip_file(zip_path: str) -> Dict[str, str]:
    """
    Extracts a .zip file and reads its contents.

    Args:
        zip_path (str): The path to the uploaded .zip file.

    Returns:
        Dict[str, str]: A dictionary mapping file paths (relative to zip root) to their contents.
    """
    file_contents = {}
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, temp_dir)

                    # Basic filtering for code files
                    if any(rel_path.endswith(ext) for ext in ['.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css']):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                file_contents[rel_path] = f.read()
                        except UnicodeDecodeError:
                            # Skip binary or non-text files
                            continue
    except zipfile.BadZipFile:
        raise RepoIngestionError(f"Invalid or corrupted zip file: {zip_path}")
    except Exception as e:
        raise RepoIngestionError(f"Failed to ingest zip file: {e}")

    return file_contents

def ingest_github_repo(repo_url: str, token: str = None) -> Dict[str, str]:
    """
    Fetches the contents of a GitHub repository.

    Args:
        repo_url (str): The URL of the GitHub repository (e.g., https://github.com/owner/repo).
        token (str, optional): GitHub personal access token for private repos or rate limits.

    Returns:
        Dict[str, str]: A dictionary mapping file paths to their contents.
    """
    # Extract owner and repo name from URL
    try:
        parts = repo_url.rstrip('/').split('/')
        repo_name = f"{parts[-2]}/{parts[-1]}"
    except IndexError:
        raise RepoIngestionError(f"Invalid GitHub repository URL: {repo_url}")

    g = Github(auth=Auth.Token(token) if token else None)

    try:
        repo = g.get_repo(repo_name)
        contents = repo.get_contents("")

        file_contents = {}

        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                # Basic filtering for code files
                if any(file_content.path.endswith(ext) for ext in ['.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css']):
                    try:
                        # Decode content if it's base64 (which it usually is from the API)
                        file_contents[file_content.path] = file_content.decoded_content.decode('utf-8')
                    except UnicodeDecodeError:
                        continue
        return file_contents
    except Exception as e:
        raise RepoIngestionError(f"Failed to ingest GitHub repository: {e}")
