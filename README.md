# Python CV PDF Generator

A professional, data-driven CV generator built with Python and FPDF2. This tool allows you to maintain your professional data in a clean YAML format and generate polished, two-column PDF layouts automatically.

## Features

- **Automated Dual-Generation**: By default, the generator processes both English (cv_data.yaml) and Hungarian (cv_data_hu.yaml) versions in a single run.
- **Dynamic Layout**: Sections automatically collapse and the layout re-adjusts if specific information (such as experience, education, or interests) is omitted from the data source.
- **Customizable Labels**: All section headers (e.g., Summary, Experience, Skills) can be overridden directly within the YAML files using a labels dictionary.
- **Two-Column Design**: Professional layout featuring experience and projects in the main column, with a sidebar for skills, languages, and education.
- **Smart Filenames**: Output PDF filenames are automatically generated based on the name and role defined in the data (e.g., cv_john_doe_software_engineer.pdf).
- **Icon Integration**: Includes standardized professional icons for contact information and section highlights.

## Prerequisites

- Python 3.7+
- fpdf2
- PyYAML

## Installation

1. Clone or download this repository.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Prepare Your Data
The generator uses YAML files for input. You can use the provided examples as a starting point:
- `cv_data.yaml`: Primary data file (typically English).
- `cv_data_hu.yaml`: Secondary data file (typically Hungarian).

### 2. Generate Your CV
To generate both default CV versions at once, run:

```bash
python generator.py
```

To generate a specific CV from a custom YAML file, provide it as an argument:

```bash
python generator.py custom_data.yaml
```

## Customization

### Section Labels
You can change any section header by adding a `labels` section to your YAML file:

```yaml
labels:
  summary: "PROFESSIONAL SUMMARY"
  experience: "WORK HISTORY"
  education: "STUDIES"
```

### Profile Picture
Place your profile picture in the `assets/` directory (e.g., `assets/profile.jpg`) and reference the path in the `image` field of your YAML file.

### Icons
Standard icons are located in the `assets/` directory. The generator expects the following filenames for consistent styling:
- `phone.png`, `envelope-simple.png`, `map-pin.png`
- `github-logo.png`, `linkedin-logo.png`
- `calendar-gray.png`, `map-pin-gray.png`

## License

This project is open-source and free to use for personal career development.
