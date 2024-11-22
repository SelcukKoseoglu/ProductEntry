# Product Scraper Pipeline

A scraper pipeline that periodically processes product data from all XML files in a specified folder and updates a MongoDB database.

## Key Features

- **Modularity**: Code is divided into reusable classes and functions.
- **Efficiency**: Handles large XML files and MongoDB updates efficiently.
- **Periodicity**: Updates MongoDB at regular intervals (configurable).
- **Error Handling**: Logs and manages errors gracefully.
- **Object-Oriented**: Utilizes object-oriented principles for better maintainability.

## Components

1. **MongoDBConnection**: Manages MongoDB connection and database operations.
2. **SchedulerManager**: Encapsulates periodic task management, separating it from product-specific processing logic.
2. **ProductProcessor**: Handles product-specific XML parsing, description extraction, and MongoDB upserts, with limited MongoDB methods, so no separate database class was created.
4. **main.py**: Entry point for the program; initializes and runs the scheduler.

## Setup and Installation

### Install Dependencies

#### Using Virtual Environment (`venv`)
It is recommended to use a virtual environment to isolate your project dependencies. If you'd like to use a virtual environment, follow these steps:

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
    ```

2. **Activate the virtual environment:**:
    **Windows**:
        ```bash
        venv\Scripts\activate
        ```

    **Mac/Linux**:
        ```bash
        source venv/bin/activate
        ```
3. **Install the required dependencies:**:  
    ```bash
    pip install -r requirements.txt
    ```

#### Without Virtual Environment

If you prefer not to use a virtual environment, you can install the dependencies globally (for your system's Python):
1. **Install dependencies directly:**:  
    ```bash
    pip install -r requirements.txt
    ```

### Configure Project Settings

Make sure MongoDB is running locally or use a cloud-based instance (e.g., MongoDB Atlas). Update config.json with your MongoDB URI, database name, and other settings.

```json
{
    "mongodb": {
        "uri": "mongodb://localhost:27017/",
        "database_name": "scraper_pipeline"
    },
    "xml_folder": "file/",
    "job_interval_seconds": 10
}
```

- **uri**: The URI for connecting to MongoDB.
- **database_name**: The name of the MongoDB database where products will be stored.
- **xml_folder**: Path to the folder containing XML files with product data. The system will process all .xml files found in this directory.
- **job_interval_seconds**: Specifies the time interval, in seconds, at which the periodic job (XML processing and MongoDB update) should run. This value determines how frequently the scraper checks and processes the XML file and updates the MongoDB database. For example, setting it to 10 means the job will run every 10 seconds.


### Configure XML Files

Place all your XML files in the specified directory (e.g., file/) or update the path in the config.json file under xml_folder. The scraper will process all XML files in that folder.

## Running the Project

### Start the Periodic Job

Once everything is set up, run the following command to start processing the XML and periodically update MongoDB:

```bash
python main.py
```

This will start the scheduler and execute the job function at regular intervals.

### Stop the Job

To stop the scheduler, press Ctrl+C or terminate the script.
