# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ESV Toolbox is a Streamlit-based web application for energy data analysis and business process automation. The application is written in Polish and contains tools for:

- PTPIREE file analysis (electricity grid data)
- Energy consumption zone calculations
- Invoice approval in Microsoft Business Central
- User management with database persistence

## Architecture

This is a Python-based Streamlit application with the following structure:

- `main.py`: Main application entry point
- `src/`: Core application modules
  - `core/config.py`: Configuration management with environment variables
  - `db/`: Database operations and SQLite management
  - `ui/components/`: Streamlit UI components and user management
  - `models/`: Data models
  - `utils/`: Utility functions
  - `data/`: Data processing modules
- `pages/`: Streamlit multipage components (3 main calculators)
- `data/`: Database files and data storage
- `input/`: Input file processing directory

The application uses SQLite for user data persistence and connects to MSSQL Server for business operations.

## Development Commands

### Running the Application

**Local development:**
```bash
streamlit run main.py
```
The app will run on http://localhost:8501

**Docker (recommended):**
```bash
docker-compose up --build
```
The app will run on http://localhost:8501

### Dependencies

Install Python dependencies:
```bash
pip install -r requirements.txt
```

The application requires Python 3.11+ and uses a virtual environment in `.venv/`.

### Configuration

The application uses environment variables loaded from `.env` file:
- `DATABASE_PATH`: SQLite database location (default: "data/users.db")
- `MSSQL_*`: SQL Server connection parameters
- `DEBUG`: Debug mode toggle
- `TZ`: Timezone (default: "Europe/Warsaw")

### Database

The application uses SQLite for user management. Database file location is configured in `src/core/config.py` and defaults to `data/users.db`.

## Key Technical Details

- **Framework**: Streamlit for web UI
- **Database**: SQLite (local), MSSQL Server (business operations)
- **Language**: Polish (comments and UI text)
- **Docker**: Multi-stage build with ODBC drivers for MSSQL connectivity
- **File Structure**: Modular design with separated concerns (UI, data, models, utilities)

The codebase follows Polish naming conventions and documentation. Configuration is centralized in `src/core/config.py` with environment variable support.