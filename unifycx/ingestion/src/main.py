import json
import os
from lamda.process.json_processor import process_employee_data

def lambdaHandler(event, context):
    """
    Main handler function for Lambda execution
    
    Args:
        event (dict): Input event data containing scraper information
        context: Lambda context (unused in this implementation)
        
    Returns:
        dict: Response containing scraper execution status
    """
    try:
        # Extract scraper information from the input event
        scraper_input = event.get("scraper_input", {})
        scraper_name = scraper_input.get("scraper_name")
        run_scraper_id = scraper_input.get("run_scraper_id")
        
        if not scraper_name or not run_scraper_id:
            return {
                "statusCode": 400,
                "body": "Missing required parameters: scraper_name or run_scraper_id"
            }
        
        # Get scraper config based on scraper_name
        scraper_config = get_scraper_config(scraper_name)
        if not scraper_config:
            return {
                "statusCode": 404,
                "body": f"Scraper configuration not found for: {scraper_name}"
            }
        
        # Process the employee data
        output_data = process_employee_data(scraper_config)
        
        # Save the processed data to a local file when running locally
        output_filename = f"{scraper_name}_{run_scraper_id}.json"
        with open(output_filename, 'w') as output_file:
            json.dump(output_data, output_file, indent=2)
        
        return {
            "statusCode": 200,
            "body": f"Successfully processed employee data. Output saved to {output_filename}"
        }
        
    except Exception as e:
        print(f"Error in lambdaHandler: {str(e)}")
        return {
            "statusCode": 500,
            "body": f"Error processing request: {str(e)}"
        }

def get_scraper_config(scraper_name):
    """
    Get scraper configuration from run_scraper.json file
    
    Args:
        scraper_name (str): Name of the scraper to find
        
    Returns:
        dict: Scraper configuration or None if not found
    """
    try:
        # Load the scraper configuration from run_scraper.json
        with open('run_scraper.json', 'r') as config_file:
            scrapers = json.load(config_file)
        
        # Find the matching scraper configuration
        for scraper in scrapers:
            if scraper.get("scraper_name") == scraper_name:
                return scraper
        
        return None
    
    except Exception as e:
        print(f"Error loading scraper configuration: {str(e)}")
        return None

if __name__ == "__main__":
    # For local testing, create a test input
    inputData = {
        "scraper_input": {
            "scraper_name": "json_100",
            "run_scraper_id": "100"
        }
    }
    
    # Call the Lambda handler function
    result = lambdaHandler(inputData, "")
    print(result)