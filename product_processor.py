import json
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR
from connection import MongoDBConnection
import xml.etree.ElementTree as ET
from pymongo import UpdateOne
from bs4 import BeautifulSoup
import html
import re
from bson import ObjectId 


class ProductProcessor:
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
        product_id = product_element.attrib.get("ProductId")
        name = product_element.attrib.get("Name", "").lower().title()

        color = self.get_product_detail(product_element, "Color").capitalize()
        stock_code = f"{product_id.split('-')[0]}-{color}" if product_id and color else None

        images = [
            image.attrib.get("Path") for image in product_element.find("Images").findall("Image")
            if image.attrib.get("Path")
        ]

        details = {
            detail.attrib["Name"]: detail.attrib["Value"]
            for detail in product_element.find("ProductDetails").findall("ProductDetail")
        }

        description = product_element.find("Description").text
        desc_dict = self.extract_description(description)

        now = datetime.now()
        return {
            "_id": ObjectId(),
            "name": name,
            "stock_code": stock_code,
            "color": [color] if color else [],
            "images": images,
            "price": float(details.get("Price", "0").replace(",", ".")),
            "discounted_price": float(details.get("DiscountedPrice", "0").replace(",", ".")),
            "is_discounted": details.get("Price") != details.get("DiscountedPrice"),
            "product_type": details.get("ProductType"),
            "quantity": int(details.get("Quantity", "0")),
            "series": details.get("Series"),
            "status": "Active" if int(details.get("Quantity", "0")) > 0 else "Inactive",
            "fabric": desc_dict.get("Kumaş Bilgisi"),
            "model_measurements": desc_dict.get("Model Ölçüleri"),
            "product_measurements": desc_dict.get("Ürün Ölçüleri"),
            "sample_size": desc_dict.get("size"),
            "createdAt": now,
            "updatedAt": now
        }

    def extract_description(self, description):
        try:
            soup = BeautifulSoup(description, "html.parser")

            product_info = {}

            for li in soup.find_all("li"):
                # Başlıkları ve metinleri alıyoruz
                strong_tag = li.find("strong")
                if strong_tag:
                    title = strong_tag.text.replace(":", "").strip()  
                    text = li.text.replace(strong_tag.text, "").strip() 
                    text = html.unescape(text) 
                    text = re.sub(r'\s+', ' ', text)  
                    if text == 'Modelin üzerindeki ürün bedendir.':
                        product_info["size"] = title
                    else:
                        product_info[title] = text

            return product_info

        except Exception as e:
            print(f"Error extracting product info: {e}")
        return None

    def upsert_products(self, products, collection):
        """Insert or update products in the MongoDB collection using stock_code."""
        operations = []
        for product in products:
            product_copy = product.copy() 
            if "_id" in product_copy:
                del product_copy["_id"]

            operations.append(
                UpdateOne({"stock_code": product["stock_code"]}, {"$set": product_copy}, upsert=True)
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
            

    @staticmethod
    def get_product_detail(product_element, detail_name):
        """Retrieve specific detail from ProductDetails section."""
        for detail in product_element.find("ProductDetails").findall("ProductDetail"):
            if detail.attrib["Name"] == detail_name:
                return detail.attrib["Value"]
        return ""
