from scholaros.logging import LogManager


def test_logger_creation():
    manager = LogManager()
    assert manager.logger.name == "ScholarOS"