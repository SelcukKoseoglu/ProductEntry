import os
import json
import time
from product_processor import ProductProcessor
from scheduler_manager import SchedulerManager
from connection import MongoDBConnection


def job_function():
    processor = ProductProcessor(config_path="config.json")
    
    config = processor.load_config()
    
    xml_folder = config.get("xml_folder", "file/")
    
    xml_files = [f for f in os.listdir(xml_folder) if f.endswith('.xml')]
    
    if not xml_files:
        print(f"No XML files found in folder: {xml_folder}")
        
    
    print(f"Found {len(xml_files)} XML files: {', '.join(xml_files)}")
    
    connection = MongoDBConnection(config_path="config.json")
    try:
        db = connection.connect()
        products_collection = db["products"]
        
        for xml_file in xml_files:
            xml_file_path = os.path.join(xml_folder, xml_file)
            print(f"Processing XML file: {xml_file_path}")
            
            processor.process_xml(xml_file_path, products_collection)
    finally:
        connection.close()


if __name__ == "__main__":
    scheduler = SchedulerManager(job_function=job_function, interval_seconds=5)
    try:
        scheduler.start()
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.stop()
