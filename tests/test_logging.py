from vira import getViraLogger


def test_default_logging():
    logger = getViraLogger()

    logger.error("Unit Testing logging. Error message")
    logger.warning("Unit Testing logging. Warning message")
    logger.info("Unit Testing logging. Info message")
    logger.debug("Unit Testing logging. Debug message")
