from app import create_app
from config import config
from logger import logger

app = create_app()

if __name__ == "__main__":
    logger.info("Starting Bili2Text web server on %s:%d", config.FLASK_HOST, config.FLASK_PORT)
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG,
    )
