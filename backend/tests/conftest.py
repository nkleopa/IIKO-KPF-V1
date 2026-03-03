import os

# Set dummy env vars before any app imports so Settings() can instantiate
# without requiring real credentials. Tests that need real iiko access are
# integration tests and are not run here.
os.environ.setdefault("IIKO_HOST", "test.example.com")
os.environ.setdefault("IIKO_LOGIN", "test_login")
os.environ.setdefault("IIKO_PASSWORD", "test_password")
