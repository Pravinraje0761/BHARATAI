"""Zero-Cost, Lightweight SQLite Authentication Engine for BHARATGURU.

Features:
- 100% free local storage (no paid cloud auth / Firebase / Cognito required).
- PBKDF2-HMAC-SHA256 salted password hashing (100,000 rounds) using Python stdlib.
- Bearer session token management with SQLite persistence and TTL.
- Role-based accounts: 'student' and 'teacher'.
- Pre-seeded instant 1-click demo accounts:
    * Student: "aarav" (password: "student123")
    * Teacher: "priya" (password: "teacher123")
"""
from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Any

import config

_AUTH_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    username            TEXT UNIQUE NOT NULL,
    email               TEXT UNIQUE NOT NULL,
    password_hash       TEXT NOT NULL,
    salt                TEXT NOT NULL,
    full_name           TEXT NOT NULL,
    role                TEXT NOT NULL DEFAULT 'student',
    grade_or_board      TEXT DEFAULT 'CBSE Class 10',
    preferred_language  TEXT DEFAULT 'English',
    avatar_url          TEXT DEFAULT '',
    created_at          REAL NOT NULL,
    last_login          REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    token               TEXT PRIMARY KEY,
    user_id             INTEGER NOT NULL,
    username            TEXT NOT NULL,
    created_at          REAL NOT NULL,
    expires_at          REAL NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON auth_sessions(token);
"""


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()


def _sanitize_username(username: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-\.]", "", username.strip().lower())


class AuthStore:
    def __init__(self, db_path: str | Path | None = None):
        self.path = Path(db_path or config.DB_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_AUTH_SCHEMA)
        self.conn.commit()
        self._seed_default_accounts()

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass

    def _user_dict(self, row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        d = dict(row)
        d.pop("password_hash", None)
        d.pop("salt", None)
        return d

    def _seed_default_accounts(self):
        """Seed demo student ('aarav') and teacher ('priya') accounts if not present."""
        now = time.time()

        # 1. Demo Student
        if not self.get_user_by_username("aarav"):
            salt = secrets.token_hex(16)
            phash = _hash_password("student123", salt)
            self.conn.execute(
                """
                INSERT INTO users 
                (username, email, password_hash, salt, full_name, role, grade_or_board, preferred_language, avatar_url, created_at, last_login)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "aarav",
                    "aarav.patel@bharatguru.edu",
                    phash,
                    salt,
                    "Aarav Patel",
                    "student",
                    "CBSE Class 10",
                    "English",
                    "👨‍🎓",
                    now,
                    now,
                ),
            )

        # 2. Demo Teacher
        if not self.get_user_by_username("priya"):
            salt = secrets.token_hex(16)
            phash = _hash_password("teacher123", salt)
            self.conn.execute(
                """
                INSERT INTO users 
                (username, email, password_hash, salt, full_name, role, grade_or_board, preferred_language, avatar_url, created_at, last_login)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "priya",
                    "dr.priya@bharatguru.edu",
                    phash,
                    salt,
                    "Dr. Priya Sharma",
                    "teacher",
                    "Faculty of Physics",
                    "English",
                    "👩‍🏫",
                    now,
                    now,
                ),
            )

        # 3. Default student1 account (backward compatibility)
        if not self.get_user_by_username("student1"):
            salt = secrets.token_hex(16)
            phash = _hash_password("student123", salt)
            self.conn.execute(
                """
                INSERT INTO users 
                (username, email, password_hash, salt, full_name, role, grade_or_board, preferred_language, avatar_url, created_at, last_login)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "student1",
                    "student1@bharatguru.edu",
                    phash,
                    salt,
                    "Student One",
                    "student",
                    "CBSE Class 10",
                    "English",
                    "🎓",
                    now,
                    now,
                ),
            )

        # 4. Seed rich demo learning data for 'aarav' if not yet populated
        kg_count = self.conn.execute(
            "SELECT COUNT(*) FROM student_knowledge_graph WHERE student = 'aarav'"
        ).fetchone()[0]
        if kg_count == 0:
            demo_concepts = [
                ("Electric Current", "Electricity", 0.92, 0.95, "[]", 5, 5, "analogy", "English"),
                ("Potential Difference (Voltage)", "Electricity", 0.85, 0.88, "[]", 4, 4, "analogy", "English"),
                ("Resistance and Ohm's law", "Electricity", 0.78, 0.80, "[\"Confuses resistance with resistivity\"]", 5, 4, "socratic", "English"),
                ("Joule Heating & Electric Power", "Electricity", 0.65, 0.70, "[\"Assumes higher resistance always increases current\"]", 3, 2, "cricket", "English"),
                ("Newton's First Law & Inertia", "Mechanics", 0.95, 0.98, "[]", 6, 6, "real_life", "English"),
                ("Newton's Second Law (F = ma)", "Mechanics", 0.82, 0.85, "[]", 4, 3, "socratic", "English"),
            ]
            for c in demo_concepts:
                self.conn.execute(
                    """
                    INSERT OR REPLACE INTO student_knowledge_graph
                    (student, concept, domain, mastery, confidence, misconceptions, attempts, successes, preferred_style, language, last_attempt)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "aarav",
                        c[0],
                        c[1],
                        c[2],
                        c[3],
                        c[4],
                        c[5],
                        c[6],
                        c[7],
                        c[8],
                        now - 86400,
                    ),
                )

        # Seed sample session for aarav
        sess_count = self.conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE student = 'aarav'"
        ).fetchone()[0]
        if sess_count == 0:
            self.conn.execute(
                """
                INSERT INTO sessions 
                (student, topic, language, level, score, out_of, strong, weak, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "aarav",
                    "Chapter 12: Electricity & Ohm's Law",
                    "English",
                    "CBSE Class 10",
                    4.0,
                    5.0,
                    '["Electric Current", "Potential Difference (Voltage)"]',
                    '["Joule Heating & Electric Power"]',
                    now - 86400,
                ),
            )

        self.conn.commit()

    def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        u = _sanitize_username(username)
        row = self.conn.execute(
            "SELECT * FROM users WHERE LOWER(username) = ?", (u,)
        ).fetchone()
        return self._user_dict(row)

    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        em = email.strip().lower()
        row = self.conn.execute(
            "SELECT * FROM users WHERE LOWER(email) = ?", (em,)
        ).fetchone()
        return self._user_dict(row)

    def get_user_by_id(self, user_id: int) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return self._user_dict(row)

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role: str = "student",
        grade_or_board: str = "CBSE Class 10",
        preferred_language: str = "English",
        avatar_url: str = "",
    ) -> dict[str, Any]:
        username = _sanitize_username(username)
        email = email.strip().lower()

        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        if "@" not in email or "." not in email:
            raise ValueError("Please provide a valid email address.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")

        role = role.lower()
        if role not in ("student", "teacher"):
            role = "student"

        # Check existing
        existing = self.conn.execute(
            "SELECT id FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?",
            (username, email),
        ).fetchone()
        if existing:
            raise ValueError("A user with this username or email already exists.")

        salt = secrets.token_hex(16)
        phash = _hash_password(password, salt)
        now = time.time()
        if not avatar_url:
            avatar_url = "👨‍🎓" if role == "student" else "👩‍🏫"

        cur = self.conn.execute(
            """
            INSERT INTO users 
            (username, email, password_hash, salt, full_name, role, grade_or_board, preferred_language, avatar_url, created_at, last_login)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                email,
                phash,
                salt,
                full_name.strip() or username,
                role,
                grade_or_board.strip() or "CBSE Class 10",
                preferred_language.strip() or "English",
                avatar_url,
                now,
                now,
            ),
        )
        self.conn.commit()
        user_id = cur.lastrowid
        return self.get_user_by_id(user_id)  # type: ignore

    def authenticate_user(
        self, username_or_email: str, password: str
    ) -> dict[str, Any] | None:
        clean = username_or_email.strip().lower()
        row = self.conn.execute(
            "SELECT * FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?",
            (clean, clean),
        ).fetchone()
        if not row:
            return None

        salt = row["salt"]
        stored_hash = row["password_hash"]
        check_hash = _hash_password(password, salt)

        if not hmac.compare_digest(stored_hash, check_hash):
            return None

        # Update last login
        now = time.time()
        self.conn.execute(
            "UPDATE users SET last_login = ? WHERE id = ?", (now, row["id"])
        )
        self.conn.commit()

        return self._user_dict(row)

    def create_session(self, user_id: int, ttl_days: int = 30) -> str:
        token = secrets.token_urlsafe(32)
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} does not exist.")

        now = time.time()
        expires_at = now + (ttl_days * 86400)

        self.conn.execute(
            """
            INSERT INTO auth_sessions (token, user_id, username, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (token, user_id, user["username"], now, expires_at),
        )
        self.conn.commit()
        return token

    def get_user_by_token(self, token: str) -> dict[str, Any] | None:
        if not token:
            return None
        now = time.time()
        row = self.conn.execute(
            """
            SELECT u.*, s.expires_at 
            FROM auth_sessions s 
            JOIN users u ON s.user_id = u.id 
            WHERE s.token = ? AND s.expires_at > ?
            """,
            (token, now),
        ).fetchone()
        if not row:
            return None
        return self._user_dict(row)

    def invalidate_session(self, token: str) -> bool:
        cur = self.conn.execute(
            "DELETE FROM auth_sessions WHERE token = ?", (token,)
        )
        self.conn.commit()
        return cur.rowcount > 0

    def update_profile(self, user_id: int, updates: dict[str, Any]) -> dict[str, Any] | None:
        allowed = {"full_name", "grade_or_board", "preferred_language", "avatar_url"}
        filtered = {k: v for k, v in updates.items() if k in allowed}
        if not filtered:
            return self.get_user_by_id(user_id)

        set_clauses = [f"{k} = ?" for k in filtered.keys()]
        values = list(filtered.values()) + [user_id]

        self.conn.execute(
            f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?",
            values,
        )
        self.conn.commit()
        return self.get_user_by_id(user_id)


# Singleton instance helper
_AUTH_STORE: AuthStore | None = None


def get_auth_store() -> AuthStore:
    global _AUTH_STORE
    if _AUTH_STORE is None:
        _AUTH_STORE = AuthStore()
    return _AUTH_STORE
