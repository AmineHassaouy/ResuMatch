# ResuMatch

> **ResuMatch** is a Python-based project designed to parse resumes and match skills with job requirements. It simplifies the recruitment process by automating the extraction and comparison of skills from resumes and job descriptions.

---

## ✨ Features

- **Resume Parsing**: Extracts structured data from resumes (e.g., skills, experience, education).
- **Skill Matching**: Compares extracted skills with job requirements to identify the best matches.
- **Database Integration**: Stores and retrieves parsed resume data efficiently.
- **User Interface**: A simple UI to interact with the system (located in the `ui` directory).

---

## 📂 Project Structure

```plaintext
ResuMatch/
├── ui/                  # User interface components
├── database.py          # Database operations and configurations
├── main.py              # Main application entry point
├── resume_parser.py     # Logic for parsing resumes
├── skill_matcher.py     # Logic for matching skills with job requirements
├── requirements.txt     # Python dependencies
└── .gitignore           # Files and directories ignored by Git
```

---

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone the Repository**:
  ```bash
   git clone https://github.com/AmineHassaouy/ResuMatch.git
   cd ResuMatch
  ```
2. **Install Dependencies**:
  ```bash
   pip install -r requirements.txt
  ```
3. **Set Up the Database**:
  - Ensure you have the required database system installed (e.g., SQLite, PostgreSQL).
  - Update the database configuration in `database.py` if necessary.

---

## 🚀 Usage

1. **Run the Application**:
  ```bash
   python main.py
  ```
2. **Interact with the UI**:
  - Navigate to the `ui` directory and follow the instructions to launch the user interface.
3. **Parse a Resume**:
  - Use the `resume_parser.py` script to parse a resume file and extract structured data.
4. **Match Skills**:
  - Use the `skill_matcher.py` script to compare extracted skills with job requirements.

---

## 📦 Dependencies

All required Python packages are listed in `requirements.txt`. Install them using:

```bash
pip install -r requirements.txt
```

---

## 🤝 Contributing

Contributions are welcome! Here’s how you can help:

1. **Fork the Repository**: Create a fork of this repository.
2. **Create a Branch**: Make your changes in a new branch.
3. **Submit a Pull Request**: Open a pull request to merge your changes.

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 📞 Contact

For questions or feedback, feel free to reach out:

- **GitHub**: [AmineHassaouy](https://github.com/AmineHassaouy)
- **Email**: [amine.hassaouy@example.com](mailto:amine.hassaouy@example.com) *(replace with your actual email)*