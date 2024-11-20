import time
from product_scheduler import ProductScheduler

# Main execution
if __name__ == "__main__":
    scheduler = ProductScheduler(config_path="config.json")
    try:
        scheduler.start(interval_minutes=10)  
        while True:
            time.sleep(1)  
    except (KeyboardInterrupt, SystemExit):
        scheduler.stop()
