from app.config import load_settings
from app.scheduler import run_scheduler


if __name__ == "__main__":
    run_scheduler(load_settings())
