## Project structure

```text
AttendIQ/
├── app.py                         # Streamlit application entry point
├── requirements.txt               # Python dependencies
├── tests/
│   └── test_teacher_flow.py       # Teacher, student, recognition and DB tests
└── src/
    ├── components/                # Dialogs, cards, header and footer
    ├── database/
    │   ├── config.py              # Supabase client configuration
    │   ├── db.py                  # Database queries and mutations
    │   └── dbCreation.sql         # PostgreSQL schema
    ├── pipelines/
    │   ├── facePipeline.py        # Face embedding and recognition pipeline
    │   └── voicePipeline.py       # Voice embedding and matching pipeline
    ├── screens/                   # Home, teacher and student screens
    └── ui/                        # Shared professional styling
```

## Local setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd <repository-directory>
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Git Bash:

```bash
python -m venv venv
source venv/Scripts/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Native face-recognition dependencies can take additional time to install. Ensure that the Python version and platform have compatible dlib packages available.

### 4. Create the Supabase database

1. Create a new Supabase project.
2. Open its SQL Editor.
3. Run [`src/database/dbCreation.sql`](src/database/dbCreation.sql).
4. Copy the project URL and API key from the Supabase project settings.

The schema creates these tables:

- `teachers`
- `students`
- `subjects`
- `subject_student`
- `attendance_logs`

### 5. Configure Streamlit secrets

Create `.streamlit/secrets.toml` locally:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-key"
```

Do not commit real credentials. The `.streamlit` directory is excluded by this project's `.gitignore`.

### 6. Start the application

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal, normally `http://localhost:8501`.

## Running tests

```bash
python -m unittest tests.test_teacher_flow -v
```

The suite covers teacher login redirection, photo handling, strict single-student face verification, attendance downloads, subject queries, session summaries, enrollment, and student dashboard behavior.

## Deployment on Streamlit Community Cloud

1. Push the project to a Git repository.
2. Create a Streamlit Community Cloud application using `app.py` as the entry point.
3. Add `SUPABASE_URL` and `SUPABASE_KEY` to the application's Secrets settings.
4. Deploy and verify camera/microphone permissions over HTTPS.

## Security and privacy

AttendIQ processes biometric embeddings and attendance records. For production or institutional use:

- obtain informed consent before collecting face or voice data;
- configure Supabase Row Level Security and least-privilege policies;
- use an appropriate server-side Supabase key rather than exposing administrative credentials;
- define retention and deletion policies for biometric data;
- restrict teacher access and audit attendance changes;
- comply with applicable privacy, education, and biometric-data regulations.

## Current limitation

Attendance sessions are identified by the shared timestamp written for one analysis run. A future schema can introduce a dedicated `attendance_sessions` table for session names, lecture topics, editing, and stronger reporting.

---

Built with Streamlit, Supabase, face recognition, and voice verification.
Filter files
