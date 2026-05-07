from database import inicializar_db
import os
import database
import pytest
import sqlite3
import gc

@pytest.fixture
def fixture_inicializar_db():
    """Fixture para los test de las bases de datos"""
    database.DB_NAME = "test.db"
    inicializar_db()

    yield

    gc.collect()
    sqlite3.connect("test.db").close()
    os.remove("test.db")