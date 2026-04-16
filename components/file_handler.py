# Implements SRS FR-1.1 (File Upload), FR-1.4 (Data Storage)
"""
FileHandler Component
---------------------
Handles file upload, validation, and storage operations.
Accepts CSV files up to 10MB and saves them to the uploads/ folder.
"""

import os
from datetime import datetime
from werkzeug.utils import secure_filename

# Constants — no magic numbers allowed (see CLAUDE.md coding rules)
UPLOAD_FOLDER = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
ALLOWED_EXTENSIONS = {".csv"}


class FileHandler:
    """Handles all file upload and storage operations."""

    def __init__(self):
        """Set upload folder path and create it if it does not exist."""
        self.upload_folder = UPLOAD_FOLDER
        os.makedirs(self.upload_folder, exist_ok=True)

    def validate_file(self, file):
        """
        Check whether an uploaded file is valid.

        Validation rules (SRS FR-1.1):
        - File must exist and have a name
        - Extension must be .csv
        - Size must not exceed 10MB

        Args:
            file: Werkzeug FileStorage object from Flask's request.files.

        Returns:
            Tuple (True, "") if valid, or (False, "error message") if not.
        """
        # Check a file was actually selected
        if file is None or file.filename == "":
            return False, "No file selected. Please choose a CSV file."

        # Check file extension
        _, ext = os.path.splitext(file.filename)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            return False, "Invalid file type. Only .csv files are accepted."

        # Check file size by seeking to end, reading position, then resetting
        # seek(0, 2) means: move to 0 bytes from the end of the file
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)  # Reset pointer so the file can still be read after this
        if size > MAX_FILE_SIZE:
            return False, "File exceeds the 10MB size limit."

        return True, ""

    def save_file(self, file):
        """
        Save uploaded file to the uploads/ folder with a timestamped name.

        Uses secure_filename() to strip any dangerous characters from the name.
        secure_filename explanation: turns unsafe names like "../../hack.csv"
        into safe ones like "hack.csv" before saving to disk.

        Args:
            file: Werkzeug FileStorage object.

        Returns:
            Generated filename string if successful, or None on failure.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = secure_filename(f"properties_{timestamp}.csv")
            filepath = os.path.join(self.upload_folder, filename)
            file.save(filepath)
            return filename
        except Exception:
            return None

    def get_file_path(self, filename):
        """
        Return the full path for a saved file.

        Args:
            filename: The saved filename string.

        Returns:
            Full file path string.
        """
        return os.path.join(self.upload_folder, filename)

    def delete_file(self, filename):
        """
        Delete a file from the uploads/ folder.
        Called to clean up invalid files after a failed data validation.

        Args:
            filename: The filename to delete.

        Returns:
            True if deleted successfully, False if an error occurred.
        """
        try:
            filepath = self.get_file_path(filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            return True
        except Exception:
            return False
