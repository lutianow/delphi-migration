# Delphi Migration Studio (Pods Theme) 🚀

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Language](https://img.shields.io/badge/language-pt--BR%20%7C%20en--US-yellow.svg)

A professional, open-source tool built to automate the complex process of migrating legacy **Delphi 7** projects to modern environments like **Delphi 12 Athens**.

Featuring a stunning, Dribbble-inspired dark mode UI, seamless internationalization (i18n), and a decoupled modular engine designed for enterprise codebases.

---

## ✨ Features

*   **Dribbble "Pods" UI/UX:** A beautiful, responsive interface built with `customtkinter`. Includes vibrant nested cards, a styled dashboard, and a dedicated settings view.
*   **Intelligent Migration Engine:**
    *   **BDE to FireDAC Conversion:** Automatically finds legacy BDE dependencies (e.g., `TQuery`, `DBTables`) and injects modern FireDAC equivalents.
    *   **Unit Scope Injection:** Automatically maps and injects `System.`, `Vcl.`, etc., into your `uses` clauses to ensure compatibility with Delphi XE2+.
*   **Encoding Normalization:** Automatically converts legacy `Windows-1252` (ANSI) source files to `UTF-8` to preserve complex Latin accents instantly.
*   **Native i18n Support:** Easily switch between English and Portuguese via decoupled JSON locale dictionary packages (`src/locales/`).
*   **Safe Execution:** Non-destructive processing. Operates strictly by creating an insulated copy of your legacy project into a new Workspace.

---

## 🏗️ Architecture Stack

This tool evolved from a flat script to a robust, scalable architecture using the **MVC Pattern**:

```
delphi-migration/
├── src/
│   ├── core/              # Headless Core Logic
│   │   ├── engine.py      # Main pipeline orchestration
│   │   ├── constants.py   # Regex rules and Component lookup tables
│   │   └── i18n.py        # Locale Parser and Translation manager
│   ├── gui/               # Frontend
│   │   └── app.py         # CustomTkinter interface
│   ├── locales/           # i18n Dictionary mapping
│   │   ├── en.json
│   │   └── pt.json
│   ├── utils/             # Cross-cutting file manipulators
│   └── main.py            # Entry point
```

---

## 🚀 Getting Started

You can run this project directly from the source code or build it into a standalone executable.

### 1. Requirements

*   Python 3.11 or higher
*   `customtkinter` library

### 2. Installation (From Source)

```bash
# Clone the repository
git clone https://github.com/lutianow/delphi-migration.git
cd delphi-migration

# Install dependencies
pip install customtkinter

# Run the application
python src/main.py
```

### 3. Building the Executable (.exe)

Want to distribute it to colleagues without installing python? Build an executable using PyInstaller:

```bash
pip install pyinstaller

# Build a standalone executable including the i18n JSON packages:
py -m PyInstaller --noconsole --onefile --add-data "src\locales\*.json;src\locales" src\main.py --name "Migrador_Modular_I18N"
```
The final binary will be available in the `dist/` folder.

---

## 🤝 Contributing

Contributions are always welcome. Feel free to open issues or submit Pull Requests for extra component mappings, new feature suggestions, or syntax edge cases.

**MIT License** - Made with ❤️ by Luciano and Antigravity.
