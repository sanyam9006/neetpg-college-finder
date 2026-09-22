import os
import sqlite3
import hashlib
import secrets
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator
import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

import io
import csv
from fastapi.responses import StreamingResponse

ADMIN_KEY = os.environ.get("ADMIN_KEY", "neetpg_admin_2024")
DB_PATH = os.environ.get("DB_PATH", os.path.join("data", "users.db"))
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


class UnifiedCursor:
    def __init__(self, raw_cursor, is_postgres: bool):
        self._cursor = raw_cursor
        self.is_postgres = is_postgres
        self.lastrowid = None

    def execute(self, sql: str, params: tuple = ()):
        if self.is_postgres:
            pg_sql = sql.replace("?", "%s")
            self._cursor.execute(pg_sql, params)
        else:
            self._cursor.execute(sql, params)
            self.lastrowid = self._cursor.lastrowid
        return self

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [dict(r) for r in rows]


class UnifiedConnection:
    def __init__(self, raw_conn, is_postgres: bool):
        self._conn = raw_conn
        self.is_postgres = is_postgres

    def cursor(self):
        return UnifiedCursor(self._conn.cursor(), self.is_postgres)

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def get_db():
    if DATABASE_URL:
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            unified = UnifiedConnection(conn, is_postgres=True)
            try:
                yield unified
            finally:
                unified.close()
            return
        except Exception as e:
            print(f"Warning: PostgreSQL connection error: {e}. Falling back to SQLite.")

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    unified = UnifiedConnection(conn, is_postgres=False)
    try:
        yield unified
    finally:
        unified.close()


def init_db():
    if DATABASE_URL:
        try:
            import psycopg2
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            name TEXT NOT NULL,
                            email TEXT UNIQUE NOT NULL,
                            phone TEXT UNIQUE NOT NULL,
                            batch_year TEXT NOT NULL,
                            password_hash TEXT NOT NULL,
                            salt TEXT NOT NULL,
                            token TEXT UNIQUE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """)
                conn.commit()
            print("Connected to PostgreSQL and verified users table schema.")
            return
        except Exception as e:
            print(f"PostgreSQL initialization failed ({e}), falling back to SQLite.")

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                batch_year TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                token TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()


# Initialize database table on import
init_db()


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if not salt:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations=100_000
    ).hex()
    return pw_hash, salt


# Schemas
class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full Name of Doctor / Candidate")
    email: str = Field(..., description="Valid Email Address")
    phone: str = Field(..., min_length=10, max_length=15, description="10-digit Mobile / WhatsApp Number")
    batch_year: str = Field(..., description="MBBS Batch Year, e.g. '2020' or '2021 (Intern)'")
    password: str = Field(..., min_length=6, description="Account Password")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if not EMAIL_REGEX.match(v_clean):
            raise ValueError("Invalid email address format.")
        return v_clean


class UserLoginRequest(BaseModel):
    email_or_phone: str = Field(..., description="Registered Email Address or Phone Number")
    password: str = Field(..., min_length=6, description="Account Password")


class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    batch_year: str
    token: str
    created_at: str


class AuthResponse(BaseModel):
    status: str
    message: str
    user: UserProfileResponse


@router.post("/register", response_model=AuthResponse)
def register(req: UserRegisterRequest, db = Depends(get_db)):
    email_clean = req.email.strip().lower()
    phone_clean = req.phone.strip().replace(" ", "").replace("-", "")

    # Check if user already exists
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ? OR phone = ?", (email_clean, phone_clean))
    existing = cursor.fetchone()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="A candidate with this email address or phone number is already registered. Please login."
        )

    pw_hash, salt = hash_password(req.password)
    token = secrets.token_hex(32)
    created_at = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO users (name, email, phone, batch_year, password_hash, salt, token, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING id
    """, (req.name.strip(), email_clean, phone_clean, req.batch_year.strip(), pw_hash, salt, token, created_at))
    row = cursor.fetchone()
    db.commit()
    user_id = row["id"] if (row and "id" in row) else (cursor.lastrowid or 1)

    user_profile = UserProfileResponse(
        id=user_id,
        name=req.name.strip(),
        email=email_clean,
        phone=phone_clean,
        batch_year=req.batch_year.strip(),
        token=token,
        created_at=created_at
    )

    return AuthResponse(
        status="success",
        message="Candidate registered successfully!",
        user=user_profile
    )


@router.post("/login", response_model=AuthResponse)
def login(req: UserLoginRequest, db = Depends(get_db)):
    ident = req.email_or_phone.strip().lower()
    phone_ident = req.email_or_phone.strip().replace(" ", "").replace("-", "")

    cursor = db.cursor()
    cursor.execute("""
        SELECT id, name, email, phone, batch_year, password_hash, salt, created_at
        FROM users
        WHERE email = ? OR phone = ?
    """, (ident, phone_ident))
    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=401, detail="Invalid email/phone or password.")

    stored_hash = row["password_hash"]
    salt = row["salt"]
    test_hash, _ = hash_password(req.password, salt)

    if test_hash != stored_hash:
        raise HTTPException(status_code=401, detail="Invalid email/phone or password.")

    # Refresh session token
    new_token = secrets.token_hex(32)
    cursor.execute("UPDATE users SET token = ? WHERE id = ?", (new_token, row["id"]))
    db.commit()

    user_profile = UserProfileResponse(
        id=row["id"],
        name=row["name"],
        email=row["email"],
        phone=row["phone"],
        batch_year=row["batch_year"],
        token=new_token,
        created_at=str(row["created_at"])
    )

    return AuthResponse(
        status="success",
        message="Login successful!",
        user=user_profile
    )


@router.get("/me", response_model=UserProfileResponse)
def get_current_user(authorization: Optional[str] = Header(None), db = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing.")

    token = authorization.replace("Bearer ", "").strip()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, email, phone, batch_year, token, created_at FROM users WHERE token = ?", (token,))
    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=401, detail="Invalid or expired session token.")

    return UserProfileResponse(
        id=row["id"],
        name=row["name"],
        email=row["email"],
        phone=row["phone"],
        batch_year=row["batch_year"],
        token=row["token"],
        created_at=str(row["created_at"])
    )


admin_bearer = HTTPBearer(auto_error=False)


def verify_admin(credentials: Optional[HTTPAuthorizationCredentials] = Depends(admin_bearer)):
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Missing or invalid Authorization Bearer header.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if credentials.credentials != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid Admin Key.")
    return True


@router.get("/users")
def get_all_registered_users(
    _: bool = Depends(verify_admin),
    db = Depends(get_db)
):
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, name, email, phone, batch_year, created_at
        FROM users
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    users = [
        {
            "id": r["id"],
            "name": r["name"],
            "email": r["email"],
            "phone": r["phone"],
            "batch_year": r["batch_year"],
            "created_at": str(r["created_at"])
        }
        for r in rows
    ]
    return {"status": "success", "count": len(users), "users": users}


@router.get("/users/export")
def export_registered_users_csv(
    _: bool = Depends(verify_admin),
    db = Depends(get_db)
):
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, name, email, phone, batch_year, created_at
        FROM users
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Full Name", "Email Address", "Phone Number", "MBBS Batch Year", "Registration Date"])
    for r in rows:
        writer.writerow([r["id"], r["name"], r["email"], r["phone"], r["batch_year"], r["created_at"]])
    
    output.seek(0)
    filename = f"neetpg_candidates_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.csv"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

