# Python CV PDF Generator

A professional, data-driven CV generator built with Python and FPDF2. This tool allows you to maintain your CV data in a clean YAML format and generate a polished, two-column PDF layout automatically.

## Features

- **Data-Driven**: Manage all your professional information in a single `cv_data.yaml` file.
- **Two-Column Layout**: Professional design with a main focus on experience and projects, and a sidebar for skills, languages, and education.
- **Visual Enhancements**: Includes modern icons for contact info, experience dates, locations, and social links.
- **Dynamic Skill Tags**: Skills and interests are rendered as clean, bordered cards/tags.
- **SEO-Friendly Filenames**: Automatically generates the output PDF filename based on your name and role (e.g., `cv_john_doe_software_engineer.pdf`).
- **ASCII Normalization**: Handles special characters and accents in filenames for better compatibility.

## Example Output

You can see an example generated CV here: [example_cv.pdf](example_cv.pdf)

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

1. Open `cv_data.yaml` and fill in your professional details, including experience, projects, skills, and contact information.
2. Add your profile picture (optional) to `assets/profile.jpg`.
3. Run the generator script:

```bash
python generator.py
```

The generator will create a PDF file in the root directory following the naming convention: `cv_[your_name]_[your_role].pdf`.

## Customization

### Section Spacing
The generator uses standardized vertical spacing (5mm) between sections in the right column to ensure a balanced layout. You can adjust the `SECTION_GAP` logic within `generator.py` if needed.

### Icons
Place any custom icons in the `assets/` directory. The generator currently supports:
- `phone.png`
- `envelope-simple.png`
- `map-pin.png`
- `github-logo.png`
- `linkedin-logo.png`
- `calendar-gray.png`
- `map-pin-gray.png`
- `github-logo-gray.png`

## License

This project is open-source and free to use for personal career development.
