import logging
import time
from sqlalchemy import event
from sqlalchemy.engine import Engine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('sql.log')
    ]
)

logger = logging.getLogger('sqlalchemy.engine')


@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())
    logger.debug("SQL: %s", statement)
    logger.debug("Parameters: %s", parameters)


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    logger.debug("Total execution time: %.3f ms", total * 1000)
    if total > 0.1:
        logger.warning("Slow query detected (%.3f ms): %s", total * 1000, statement)
