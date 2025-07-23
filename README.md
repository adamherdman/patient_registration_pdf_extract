# Patient Registration PDF Extract

## Overview

This script extracts structured data from PDF forms using precise positional text mapping with `pdfplumber`. It is specifically designed to work with patient registration documents that follow a known layout.

It:

- Identifies predefined fields (e.g., "First name", "Postcode") using spatial information.
- Recognises section headers to understand context.
- Extracts values based on positional heuristics (e.g., same line, next line, separate column).
- Outputs the collected data into a clean, organised JSON file.

---

## Requirements

### Python Version

Python 3.7+

### Dependencies

Install required Python packages using pip:

```bash
pip install pdfplumber
```

---

## Directory Structure

```
project_folder/
├── pdf_documents/         # Place all PDFs to be processed here
├── script.py              # The main extraction script
└── extracted_output.json  # Output JSON file created after extraction
```

---

## How It Works

### Field Configuration

- All fields to extract are defined in a `FIELDS_TO_EXTRACT` dictionary.
- Each field has:
  - One or more `labels`
  - A `section_header` to identify its document region
  - An optional `multi_line_type` for how the value is extracted:
    - `2_line`: wraps to the second line next to the label
    - `3_line`: located in a right-hand column, may span multiple lines
    - `value_below`: value appears directly under the label

### Section Recognition

- Uses a list of `MAJOR_HEADINGS` to determine the current section.
- Ensures values are extracted in the correct context.

### Extraction Methods

Each field value is located using one of:

- **Same-line search**: value is right next to the label
- **Multi-line search**: value may wrap or appear in a different position
- **Below-line search**: value is located on the next line(s) under the label

---

## Running the Script

1. Place all your target PDFs inside the `pdf_documents/` folder.
2. Run the script:

```bash
python script.py
```

3. On success, an `extracted_output.json` will be created with results.

---

## Output Format

The output JSON file structure:

```json
[
  {
    "source_file": "example.pdf",
    "extracted_data": {
      "Patient Details": {
        "patient_first_name": "John",
        "patient_last_name": "Doe"
      },
      ...
    }
  },
  ...
]
```

---

## License

MIT License (add appropriate license info if needed)

---

## Author

adam.herdman@nhs.net

