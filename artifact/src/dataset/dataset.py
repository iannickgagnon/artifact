from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
import tarfile
import requests
from tqdm import tqdm
from typing import Union


class Dataset:
    """
    Base class for all managed datasets.

    A Dataset represents a reproducible data asset with a controlled lifecycle:
    download → verify → extract → ready.

    Subclasses must define the following class attributes:

    Attributes:
        name (str): Human-readable dataset name.
        url (str): Source URL of the dataset archive.
        checksum (str): Expected MD5 checksum of the archive for integrity validation.
        archive_name (str): Filename used to store the downloaded archive locally.
        extracted_dir (str): Directory name created when the archive is extracted.

    Instance Attributes:
        root (Path): Root directory where all dataset files are stored.
        manifest_path (Path): Path to the dataset manifest file.
    """
    name: str
    url: str
    checksum: str
    archive_name: str
    extracted_dir: str

    def __init__(self, root: Union[Path, str] = "datasets/data"):
        """
        Initializes the dataset manager.

        Args:
            root (Path | str): Root directory where dataset files are stored.
        """
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.root / f"{self.name.lower().replace(' ', '_')}.manifest.json"

    @property
    def archive_path(self) -> Path:
        """
        Returns the path to the downloaded dataset archive.
        """
        return self.root / self.archive_name

    @property
    def extracted_path(self) -> Path:
        """Returns the path to the extracted dataset directory."""
        return self.root / self.extracted_dir

    def prepare(self) -> Path:
        """
        Ensures that the dataset is downloaded, verified, extracted,
        and accompanied by a manifest file.

        Returns:
            Path: Path to the extracted dataset directory.

        Raises:
            RuntimeError: If checksum validation fails.
        """
        # If dataset is already prepared and manifest exists, trust the dataset state
        if self.extracted_path.exists() and self.manifest_path.exists():
            return self.extracted_path

        # Download archive if missing
        if not self.archive_path.exists():
            self._download()

        # Verify archive integrity
        self._verify()

        # Extract dataset contents
        self._extract()

        # Write manifest capturing the prepared dataset state
        self._write_manifest()

        return self.extracted_path

    def _download(self) -> None:
        """
        Downloads the dataset archive from its source URL.
        """
        print(f"Downloading {self.name} → {self.archive_path}")

        response = requests.get(self.url, stream=True)
        total = int(response.headers.get("content-length", 0))

        # Stream file to disk with progress reporting
        with open(self.archive_path, "wb") as f, tqdm(total=total, unit="B", unit_scale=True) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))

    def _verify(self) -> None:
        """
        Verifies the integrity of the downloaded archive using its checksum.

        Raises:
            RuntimeError: If the computed checksum does not match the expected value.
        """
        if self._md5(self.archive_path) != self.checksum:
            # Remove corrupted archive to force re-download on next run
            self.archive_path.unlink(missing_ok=True)
            raise RuntimeError(f"{self.name} archive checksum mismatch.")

    def _extract(self) -> None:
        """Extracts the dataset archive into the dataset root directory."""
        print(f"Extracting {self.name}…")
        with tarfile.open(self.archive_path, "r:gz") as tar:
            tar.extractall(self.root)

    def _write_manifest(self) -> None:
        """
        Writes a minimal dataset manifest capturing dataset identity and preparation state.
        """
        manifest = {
            "name": self.name,
            "source_url": self.url,
            "archive_name": self.archive_name,
            "checksum": self.checksum,
            "prepared_at": datetime.now(timezone.utc).isoformat(),
            "dataset_path": str(self.extracted_path.resolve()),
            "archive_path": str(self.archive_path.resolve()),
        }

        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    @staticmethod
    def _md5(path: Path) -> str:
        """
        Computes the MD5 checksum of a file.

        Args:
            path (Path): Path to the file.

        Returns:
            str: Hexadecimal MD5 checksum of the file.
        """
        hash_md5 = hashlib.md5()
    
        # Read file in chunks for memory efficiency
        CHUNK_SIZE = 8192
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
                hash_md5.update(chunk)

        return hash_md5.hexdigest()
