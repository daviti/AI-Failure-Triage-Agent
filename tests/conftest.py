import pytest


SAMPLE_LOG = """
2024-01-15 10:23:45 [INFO] Starting test suite: LoginFlowTest
2024-01-15 10:23:47 [ERROR] java.lang.NullPointerException
    at com.example.app.LoginActivity.onResume(LoginActivity.kt:142)
    at android.app.Instrumentation.callActivityOnResume(Instrumentation.java:1454)
2024-01-15 10:23:47 [ERROR] Test FAILED: testLoginWithValidCredentials
2024-01-15 10:23:47 [INFO] Screenshots saved to: /artifacts/screenshots/
2024-01-15 10:23:48 [INFO] Test run complete. 1 failed, 0 passed.
"""


@pytest.fixture
def sample_log() -> str:
    return SAMPLE_LOG
