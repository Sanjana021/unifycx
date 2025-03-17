# Data Pipeline Project

## Project Structure
This project is structured into two main folders: `ingestion` and `processing`. Each folder contains scripts responsible for different stages of the data pipeline.

### **1. Ingestion Folder** (`ingestion/`)
This folder handles data collection and ingestion from various sources.

#### **Files in ingestion:**
- **`scrape.py`** → Fetches raw data from APIs and stores it in the ingestion directory.
- **`config.py`** → Contains configuration details like API sources and ingestion directory settings.

---

### **2. Processing Folder** (`processing/`)
This folder processes and cleans the ingested data before storing it in a structured format.

#### **Files in processing:**
- **`processor.py`** → Cleans and normalizes data from ingestion sources.

---

### **3. General Project Files**
These files handle execution, testing, and overall project orchestration.

- **`main.py`** → Runs the entire pipeline by calling ingestion and processing scripts.
- **`tests.py`** → Contains unit tests to validate data processing and ingestion.

## How to Run the Pipeline
1. Ensure all dependencies are installed (`pandas`, `requests`, `bs4`, `pyarrow`).
2. Run the ingestion script:
   ```bash
   python ingestion/scrape.py
   ```
3. Run the processing script:
   ```bash
   python processing/processor.py
   ```

## Testing
Run unit tests to verify data processing:
```bash
python tests.py
```




