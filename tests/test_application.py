from pathlib import Path

from scholaros.kernel import ScholarOS


def test_application_creation():

    app = ScholarOS(Path("."))

    assert app.context.root_path == Path(".")