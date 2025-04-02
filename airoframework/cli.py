import os
import shutil
import sys
import subprocess

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "template")

REQUIRED_PACKAGES = ["aiogram", "alembic", "pyyaml", "sqlalchemy", "fastapi", "uvicorn", "dotenv"]

DEFAULT_MODEL = """from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    state = Column(String)
    username = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
"""

def run_command(command):
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

    os.chdir(project_name)

    print("📦 Installing dependencies...")
    run_command([sys.executable, "-m", "pip", "install"] + REQUIRED_PACKAGES)

    print("📝 Generating requirements.txt...")
    run_command(["pip", "freeze", '>', "requirements.txt"])
    os.makedirs("database", exist_ok=True)

    model_path = "database/models.py"
    if not os.path.exists(model_path):
        print("🛠️  Creating default user model...")
        with open(model_path, "w") as f:
            f.write(DEFAULT_MODEL)

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


    print("⚙️  Initializing Alembic...")
    run_command(["alembic", "init", "migrations"])

    env_path = "migrations/env.py"
    with open(env_path, "r") as f:
        env_data = f.read()

    env_data = env_data.replace(
        "from alembic import context",
        "import os\nfrom database.models import Base\nfrom alembic import context"
    )

    env_data = env_data.replace(
        "target_metadata = None",
        'config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", "sqlite:///database.db"))\n'
        "target_metadata = Base.metadata"
    )

    with open(env_path, "w") as f:
        f.write(env_data)

    print("📜 Generating initial migration...")
    run_command(["alembic", "revision", "--autogenerate", "-m", "Initial migration"])

    print("🚀 Applying migrations...")
    run_command(["alembic", "upgrade", "head"])

    print("✅ Done! Navigate to your project and start coding.")
    print(f"👉 cd {project_name} && python main.py")

if __name__ == "__main__":
    create_project()
