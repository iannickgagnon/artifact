# Artifact

Artifact is a lightweight, manifest-driven Python library for managing the lifecycle of data assets. It provides a robust framework to automate the **Download → Verify → Extract** workflow, ensuring your datasets are reproducible and verified.

## Features

* **Integrity First:** Automatic MD5 checksum validation ensures data consistency and prevents corruption.
* **Manifest Tracking:** Generates a `.json` manifest for every dataset, recording source URLs, timestamps, and absolute local paths.
* **Resume-Capable:** Smart checks skip redundant downloads and extractions if the dataset is already prepared.
* **Memory Efficient:** Streams large files and computes hashes in chunks to maintain a low memory footprint.
* **Extensible:** Simple class-based API to add new datasets in minutes.

---

## Installation

You can install **Artifact** directly from PyPI:

```bash
pip install artifact-manager
```

Alternatively, for development or to install from source:

```bash
git clone https://github.com/iannickgagnon/artifact.git
cd artifact
pip install -e .
```
---

## Usage

To manage a new dataset, simply subclass the `Dataset` base class and define its metadata.

### 1. Define your Dataset
```python
from artifact import Dataset

class CIFAR10(Dataset):
    name = "CIFAR-10"
    url = "ttps://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"
    checksum = "c587382273033f2762a15c324c438c82"
    archive_name = "cifar-10.tar.gz"
    extracted_dir = "cifar-10-batches-py"
```

### 2. Prepare and Use
```python
# Initialize and prepare
data_manager = CIFAR10(root="./data")
data_path = data_manager.prepare()
```

---

## The Manifest
After calling `.prepare()`, Artifact creates a `{dataset_name}.manifest.json` file. This acts as a "receipt" for your data, making your experiments more reproducible.

```json
{
  "name": "CIFAR-10",
  "source_url": "https://...",
  "checksum": "c587382273033f2762a15c324c438c82",
  "prepared_at": "2025-12-29T15:20:00Z",
  "dataset_path": "/home/user/project/data/cifar-10-batches-py",
  "archive_path": "/home/user/project/data/cifar-10.tar.gz"
}
```

---

## Project Structure
```text
artifact/
├── data/                  # Default directory for downloaded data
├── artifact/              # Core library logic
│   ├── __init__.py        # Expose the Dataset class
│   └── manager.py         # Main Dataset class logic
├── tests/                 # Unit tests
├── README.md              # Project documentation
└── requirements.txt       # Project dependencies
```

---

## Roadmap
- [ ] Add support for `.zip` and other formats.
- [ ] Integrate S3 and Google Drive downloaders.
- [ ] Add a CLI tool for downloading datasets via terminal.

## ⚖️ License
MIT
