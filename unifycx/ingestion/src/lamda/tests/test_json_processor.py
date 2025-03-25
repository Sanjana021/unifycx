import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to import modules properly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from process.json_processor import process_employee_data, transform_employee_data

class TestJsonProcessor(unittest.TestCase):
    
    def setUp(self):
        # Sample scraper configuration for testing
        self.scraper_config = {
            "scraper_id": "100",
            "scraper_name": "csv_100",
            "api_url": "https://api.slingacademy.com/v1/sample-data/files/employees.json"
        }
        
        # Sample raw employee data for testing
        self.sample_raw_data = {
            "employees": [
                {
                    "id": 1,
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "phone": "123-456-7890",
                    "gender": "Male",
                    "age": 30,
                    "job_title": "Software Engineer",
                    "years_of_experience": 2,
                    "salary": 75000,
                    "department": "Engineering"
                },
                {
                    "id": 2,
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "email": "jane.smith@example.com",
                    "phone": "987-654-3210x123",
                    "gender": "Female",
                    "age": 35,
                    "job_title": "Data Scientist",
                    "years_of_experience": 7,
                    "salary": 95000,
                    "department": "Data"
                },
                {
                    "id": 3,
                    "first_name": "Robert",
                    "last_name": "Johnson",
                    "email": "robert.johnson@example.com",
                    "phone": "555-123-4567",
                    "gender": "Male",
                    "age": 45,
                    "job_title": "Engineering Manager",
                    "years_of_experience": 12,
                    "salary": 120000,
                    "department": "Engineering"
                }
            ]
        }
    
    @patch('requests.get')
    def test_json_file_download(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_raw_data
        mock_get.return_value = mock_response
        
        # Call the function to process employee data
        result = process_employee_data(self.scraper_config)
        
        # Verify the API was called with the correct URL
        mock_get.assert_called_once_with(self.scraper_config["api_url"], timeout=30)
        
        # Check that metadata is included in the result
        self.assertIn("metadata", result)
        self.assertIn("data", result)
        
    @patch('requests.get')
    def test_json_file_extraction(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_raw_data
        mock_get.return_value = mock_response
        
        # Call the function to process employee data
        result = process_employee_data(self.scraper_config)
        
        # Check that data was extracted properly
        self.assertEqual(len(result["data"]), 3)
        
    def test_validate_file_type_and_format(self):
        # Transform the raw data
        transformed_data = transform_employee_data(self.sample_raw_data)
        
        # Check that the transformed data is a list
        self.assertIsInstance(transformed_data, list)
        
        # Check that each transformed employee has the required fields
        for employee in transformed_data:
            self.assertIsInstance(employee, dict)
            self.assertIn("employee_id", employee)
            self.assertIn("full_name", employee)
            self.assertIn("email", employee)
            self.assertIn("phone", employee)
            self.assertIn("designation", employee)
            
    def test_validate_data_structure(self):
        # Transform the raw data
        transformed_data = transform_employee_data(self.sample_raw_data)
        
        # Validate first employee record
        self.assertEqual(transformed_data[0]["employee_id"], 1)
        self.assertEqual(transformed_data[0]["full_name"], "John Doe")
        self.assertEqual(transformed_data[0]["designation"], "system engineer")
        self.assertEqual(transformed_data[0]["phone"], "123-456-7890")
        
        # Validate second employee record (with invalid phone)
        self.assertEqual(transformed_data[1]["phone"], "Invalid Number")
        self.assertEqual(transformed_data[1]["designation"], "senior data engineer")
        
        # Validate third employee record
        self.assertEqual(transformed_data[2]["designation"], "lead")
        
    def test_handle_missing_invalid_data(self):
        # Create a sample with missing data
        incomplete_data = {
            "employees": [
                {
                    "id": 4,
                    "first_name": "Missing",
                    "email": "missing.data@example.com",
                    "gender": "Female",
                    "job_title": "Developer"
                    # Missing other fields
                }
            ]
        }
        
        # Transform the incomplete data
        transformed_data = transform_employee_data(incomplete_data)
        
        # Check that the record was processed with default values
        self.assertEqual(len(transformed_data), 1)
        self.assertEqual(transformed_data[0]["full_name"], "Missing")  # Updated to match trimmed output
        self.assertEqual(transformed_data[0]["years_of_experience"], 0)
        self.assertEqual(transformed_data[0]["designation"], "system engineer")

if __name__ == '__main__':
    unittest.main()