import os
import shutil
import sys
import subprocess

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "template")

REQUIRED_PACKAGES = ["aiogram", "alembic", "pyyaml", "sqlalchemy"]

DEFAULT_MODEL = """from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    username = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
"""

def run_command(command):
    """Runs a shell command and handles errors."""
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def create_project():
    if len(sys.argv) < 3 or sys.argv[1] != "new":
        print("❌ Usage: airoframework new <project_name>")
        sys.exit(1)

    project_name = sys.argv[2]
    if os.path.exists(project_name):
        print(f"❌ Project '{project_name}' already exists.")
        sys.exit(1)

    print(f"📂 Creating project '{project_name}'...")
    shutil.copytree(TEMPLATE_DIR, project_name)

    # Navigate to the project directory
    os.chdir(project_name)

    # Install dependencies
    print("📦 Installing dependencies...")
    run_command([sys.executable, "-m", "pip", "install"] + REQUIRED_PACKAGES)

    # Generate requirements.txt
    print("📝 Generating requirements.txt...")
    with open("requirements.txt", "w") as f:
        f.writelines(f"{pkg}\n" for pkg in REQUIRED_PACKAGES)

    # Create .env and .env-example files
    print("🌍 Creating environment files...")
    env_content = "DATABASE_URL=sqlite:///database.db\nBOT_TOKEN=\n"
    
    for filename in [".env", ".env-example"]:
        with open(filename, "w") as f:
            f.write(env_content)

    # Create .gitignore
    print("📄 Creating .gitignore...")
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*.sqlite3

# Virtual environment
.venv/
.env

# Alembic
migrations/

# OS-specific
.DS_Store
Thumbs.db
"""

    with open(".gitignore", "w") as f:
        f.write(gitignore_content)

    # Create database directory and models file
    os.makedirs("database", exist_ok=True)

    model_path = "database/models.py"
    if not os.path.exists(model_path):
        print("🛠️  Creating default user model...")
        with open(model_path, "w") as f:
            f.write(DEFAULT_MODEL)

    # Create database/database.py
    db_path = "database/database.py"
    if not os.path.exists(db_path):
        print("🛠️  Creating database config file...")
        with open(db_path, "w") as f:
            f.write(
                'import os\n'
                'from sqlalchemy import create_engine\n'
                'from sqlalchemy.orm import sessionmaker\n'
                'from database.models import Base\n\n'
                'DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")\n'
                'engine = create_engine(DATABASE_URL)\n'
                'SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)\n\n'
                'def init_db():\n'
                '    Base.metadata.create_all(bind=engine)\n'
            )

    # Initialize Alembic
    print("⚙️  Initializing Alembic...")
    run_command(["alembic", "init", "migrations"])

    # Modify alembic/env.py to import database models and set sqlalchemy.url
    env_path = "migrations/env.py"
    with open(env_path, "r") as f:
        env_data = f.read()

    # Add imports
    env_data = env_data.replace(
        "from alembic import context",
        "import os\nfrom database.models import Base\nfrom alembic import context"
    )

    # Set sqlalchemy.url dynamically
    env_data = env_data.replace(
        "target_metadata = None",
        'config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", "sqlite:///database.db"))\n'
        "target_metadata = Base.metadata"
    )

    with open(env_path, "w") as f:
        f.write(env_data)

    # Generate initial migration
    print("📜 Generating initial migration...")
    run_command(["alembic", "revision", "--autogenerate", "-m", "Initial migration"])

    # Apply migrations
    print("🚀 Applying migrations...")
    run_command(["alembic", "upgrade", "head"])

    print("✅ Done! Navigate to your project and start coding.")
    print(f"👉 cd {project_name} && python main.py")

if __name__ == "__main__":
    create_project()
