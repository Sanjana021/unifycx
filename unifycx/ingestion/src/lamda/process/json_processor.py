import json
import requests
import time
from datetime import datetime

def process_employee_data(scraper_config):
    """
    Process employee data from the API endpoint
    
    Args:
        scraper_config (dict): Configuration for the scraper
        
    Returns:
        dict: Processed employee data
    """
    # Get the API URL from the scraper config or use the default
    api_url = scraper_config.get("api_url", "https://api.slingacademy.com/v1/sample-data/files/employees.json")
    
    # Maximum number of retry attempts
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Make the HTTP request to the API
            print(f"Attempting to fetch data from: {api_url}")
            response = requests.get(api_url, timeout=30)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON response
                raw_data = response.json()
                
                # Print the structure of the response for debugging
                print(f"API Response structure: {list(raw_data.keys()) if isinstance(raw_data, dict) else 'Not a dictionary'}")
                
                # Transform the data according to requirements
                processed_data = transform_employee_data(raw_data)
                
                # Return the processed data
                return {
                    "metadata": {
                        "processed_at": datetime.now().isoformat(),
                        "record_count": len(processed_data),
                        "source": api_url
                    },
                    "data": processed_data
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

def transform_employee_data(raw_data):
    """
    Transform and normalize the employee data according to requirements
    
    Args:
        raw_data (dict): Raw employee data from the API
        
    Returns:
        list: Transformed employee data
    """
    transformed_data = []
    
    # Extract employees data - handle different possible structures
    employees = []
    
    # Debug the structure of raw_data
    print(f"Raw data type: {type(raw_data)}")
    
    if isinstance(raw_data, dict):
        # Try different possible keys where employee data might be
        if "employees" in raw_data:
            employees = raw_data["employees"]
        elif "users" in raw_data:
            employees = raw_data["users"]
        elif "data" in raw_data:
            employees = raw_data["data"]
        elif "success" in raw_data and "data" in raw_data:
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
    
    # Print the first employee record for debugging
    if employees and len(employees) > 0:
        print(f"Sample employee record keys: {list(employees[0].keys()) if isinstance(employees[0], dict) else 'Not a dictionary'}")
    
    for employee in employees:
        try:
            # Extract required fields with appropriate data type conversion
            # Use get() with default values to handle missing fields
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
            
            # 1. Create designation based on years of experience
            if years_of_experience < 3:
                designation = "system engineer"
            elif 3 <= years_of_experience <= 5:
                designation = "data engineer"
            elif 5 < years_of_experience <= 10:
                designation = "senior data engineer"
            else:
                designation = "lead"
                
            # 2. Combine first name and last name into full name
            full_name = f"{first_name} {last_name}".strip()
            
            # 3. Check if phone number is valid
            # If phone contains 'x', mark as "Invalid Number"
            phone_value = "Invalid Number" if phone and 'x' in phone else phone
            
            # Create the transformed employee record
            transformed_employee = {
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
                "designation": designation
            }
            
            transformed_data.append(transformed_employee)
            
        except (ValueError, TypeError) as e:
            print(f"Error processing employee record: {str(e)}")
            # Skip invalid records
            continue
    
    return transformed_data
