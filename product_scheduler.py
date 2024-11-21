import json
import os
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR
from connection import MongoDBConnection
import xml.etree.ElementTree as ET
from pymongo import UpdateOne


class ProductScheduler:
    """Class to manage periodic product scraping and MongoDB updates."""
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.scheduler = BackgroundScheduler()

    def load_config(self):
        """Load the configuration file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, "r") as file:
            return json.load(file)

    def parse_product(self, product_element):
        """Parse a single product XML element into a dictionary."""
        product = {}
        product["_id"] = product_element.attrib.get("ProductId")
        product["name"] = product_element.attrib.get("Name").capitalize()
        product["images"] = [
            image.attrib.get("Path") for image in product_element.find("Images").findall("Image")
        ]
        
        
        details = {detail.attrib["Name"]: detail.attrib["Value"] 
                   for detail in product_element.find("ProductDetails").findall("ProductDetail")}
        
        product["price"] = float(details.get("Price", "0").replace(",", "."))
        product["discounted_price"] = float(details.get("DiscountedPrice", "0").replace(",", "."))
        product["is_discounted"] = product["price"] != product["discounted_price"]
        product["product_type"] = details.get("ProductType")
        product["quantity"] = int(details.get("Quantity", "0"))
        product["color"] = [details.get("Color").capitalize()]
        product["series"] = details.get("Series")
        product["status"] = "Active" if product["quantity"] > 0 else "Inactive"
        
        
        description = product_element.find("Description").text
        product["fabric"] = self.extract_fabric_info(description)
        product["model_measurements"] = self.extract_model_measurements(description)
        product["product_measurements"] = self.extract_product_measurements(description)
        
        now = datetime.utcnow()
        product["createdAt"] = now
        product["updatedAt"] = now
        
        return product

    def extract_fabric_info(self, description):
        """Extract fabric information from the description."""
        try:
            if "Kumaş Bilgisi:" in description:
                start = description.index("Kumaş Bilgisi:") + len("Kumaş Bilgisi:")
                end = description.find("<", start)
                return description[start:end].strip()
        except ValueError:
            print("Fabric info not found in description.")
        return None

    def extract_model_measurements(self,description):
        """Extract model measurements from the description."""
        try:
            if "Model Ölçüleri:" in description:
                start = description.index("Model Ölçüleri:") + len("Model Ölçüleri:")
                end = description.find("<", start)
                return description[start:end].strip()
        except ValueError:
            print("Model measurements not found in description.")
        return None

    def extract_product_measurements(self,description):
        """Extract product measurements from the description."""
        try:
            if "Ürün Ölçüleri:" in description:
                start = description.index("Ürün Ölçüleri:") + len("Ürün Ölçüleri:")
                end = description.find("<", start)
                return description[start:end].strip()
        except ValueError:
            print("Product measurements not found in description.")
        return None

    def upsert_products(self, products, collection):
        """Insert or update products in the MongoDB collection."""
        operations = []
        for product in products:
            operations.append(
                UpdateOne({"_id": product["_id"]}, {"$set": product}, upsert=True)
            )
        if operations:
            result = collection.bulk_write(operations)
            print(f"Inserted: {result.upserted_count}, Updated: {result.modified_count}")

    def process_xml(self, xml_file, collection):
        """Process the given XML file and store the products in MongoDB."""
        tree = ET.parse(xml_file)
        root = tree.getroot()
        products = [self.parse_product(product) for product in root.findall("Product")]
        self.upsert_products(products, collection)

    def job_function(self):
        """The job function to be executed periodically."""
        print(f"Job started at {datetime.now()}")
        try:
            config = self.load_config()
            xml_file = config.get("xml_file", "products.xml")
            if not os.path.exists(xml_file):
                print(f"XML file not found: {xml_file}")
                return

            connection = MongoDBConnection(config_path=self.config_path)
            try:
                db = connection.connect()
                products_collection = db["products"]
                self.process_xml(xml_file, products_collection)
            finally:
                connection.close()
        except Exception as e:
            print(f"An error occurred during job execution: {e}")

    def error_listener(self, event):
        """Log errors that occur during job execution."""
        if event.exception:
            print(f"Job crashed: {event.exception}")
        else:
            print("Job executed successfully.")

    def start(self, interval_seconds=5):
        """Start the scheduler and add the periodic job."""
        self.scheduler.add_job(self.job_function, "interval", seconds=interval_seconds)
        self.scheduler.add_listener(self.error_listener, EVENT_JOB_ERROR)
        self.scheduler.start()
        print("Scheduler started. Press Ctrl+C to exit.")

    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        print("Scheduler stopped.")
