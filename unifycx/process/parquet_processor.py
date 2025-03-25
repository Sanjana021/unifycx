import requests
import time
import pandas as pd
from datetime import datetime
import os

def process_employee_data(scraper_config, output_file):
   
    # Get the API URL from the scraper config or use the default
    api_url = scraper_config.get("api_url", "https://api.slingacademy.com/v1/sample-data/files/employees.json")
    
    # Maximum number of retry attempts
    max_retries = scraper_config.get("retry_attempts", 3)
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Make the HTTP request to the API
            print(f"Attempting to fetch data from: {api_url}")
            response = requests.get(api_url, timeout=scraper_config.get("timeout", 30))
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON response
                raw_data = response.json()
                
                # Print the structure of the response for debugging
                print(f"API Response structure: {list(raw_data.keys()) if isinstance(raw_data, dict) else 'Not a dictionary'}")
                
                # Transform the data and save to Parquet
                metadata = transform_and_save_to_parquet(raw_data, output_file)
                
                return {
                    "metadata": metadata
                }
            else:
                print(f"Error: API returned status code {response.status_code}")
                retry_count += 1
                if retry_count >= max_retries:
                    raise Exception(f"Failed to retrieve data after {max_retries} attempts. Last status code: {response.status_code}")
                
                # Wait before retrying
                time.sleep(2)
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed to connect to API after {max_retries} attempts. Error: {str(e)}")
            
            # Wait before retrying
            time.sleep(2)
    
    raise Exception("Failed to process employee data")

def transform_and_save_to_parquet(raw_data, output_file):
  
    # Extract employees data - handle different possible structures
    employees = []
    
    if isinstance(raw_data, dict):
        # Try different possible keys where employee data might be
        if "employees" in raw_data:
            employees = raw_data["employees"]
        elif "users" in raw_data:
            employees = raw_data["users"]
        elif "data" in raw_data:
            employees = raw_data["data"]
    elif isinstance(raw_data, list):
        # The API might return a direct list of employees
        employees = raw_data
    
    # If we still don't have employee data, try to infer from the structure
    if not employees and isinstance(raw_data, dict):
        # Look for any key that contains a list which might be employee data
        for key, value in raw_data.items():
            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                print(f"Found potential employee data in key: {key}")
                employees = value
                break
    
    # If we still have no employees data, raise an error with more information
    if not employees:
        error_msg = "Could not find employee data in the API response. "
        if isinstance(raw_data, dict):
            error_msg += f"Available keys: {list(raw_data.keys())}"
        else:
            error_msg += f"Response is not a dictionary but a {type(raw_data)}"
        raise ValueError(error_msg)
    
    print(f"Found {len(employees)} employee records to process")
    
    # Transform the data
    transformed_data = []
    for employee in employees:
        try:
            # Extract required fields
            employee_id = int(employee.get("id", 0))
            first_name = str(employee.get("first_name", employee.get("firstName", "")))
            last_name = str(employee.get("last_name", employee.get("lastName", "")))
            email = str(employee.get("email", ""))
            phone = str(employee.get("phone", employee.get("phoneNumber", "")))
            gender = str(employee.get("gender", ""))
            age = int(employee.get("age", 0))
            job_title = str(employee.get("job_title", employee.get("jobTitle", "")))
            years_of_experience = int(employee.get("years_of_experience", employee.get("experience", 0)))
            salary = int(float(employee.get("salary", 0)))
            department = str(employee.get("department", ""))
            
            # Create designation based on years of experience
            if years_of_experience < 3:
                designation = "system engineer"
            elif 3 <= years_of_experience <= 5:
                designation = "data engineer"
            elif 5 < years_of_experience <= 10:
                designation = "senior data engineer"
            else:
                designation = "lead"
                
            # Combine first name and last name into full name
            full_name = f"{first_name} {last_name}".strip()
            
            # Check if phone number is valid
            phone_valid = 'x' not in phone if phone else True
            phone_value = "Invalid Number" if not phone_valid else phone
            
            transformed_data.append({
                "employee_id": employee_id,
                "full_name": full_name,
                "email": email,
                "phone": phone_value,
                "gender": gender,
                "age": age,
                "job_title": job_title,
                "years_of_experience": years_of_experience,
                "salary": salary,
                "department": department,
                "designation": designation,
                "phone_valid": phone_valid
            })
            
        except (ValueError, TypeError) as e:
            print(f"Error processing employee record: {str(e)}")
            # Skip invalid records
            continue
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(transformed_data)
    
    # Ensure data types
    df["employee_id"] = df["employee_id"].astype("int32")
    df["age"] = df["age"].astype("int32")
    df["years_of_experience"] = df["years_of_experience"].astype("int32")
    df["salary"] = df["salary"].astype("int32")
    df["phone_valid"] = df["phone_valid"].astype("bool")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    # Save to Parquet
    df.to_parquet(output_file, index=False)
    
    # Return metadata
    return {
        "processed_at": datetime.now().isoformat(),
        "record_count": len(df),
        "columns": list(df.columns),
        "output_file": output_file,
        "file_size_bytes": os.path.getsize(output_file)
    }
