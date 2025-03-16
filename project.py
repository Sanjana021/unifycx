import json
import pandas as pd


FILE_PATH = "employee.json"

def read_json_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)  
    except FileNotFoundError:
        print("File not found. Please check the file path.")
    except json.JSONDecodeError:
        print("Error decoding JSON. Ensure the file format is correct.")
    except Exception as e:
        print(f"Unexpected error while reading JSON: {e}")
    return None

def clean_phone_number(phone):
    if 'x' in phone or not phone.replace('-', '').replace('.', '').isdigit():
        return "Invalid Number"
    return int(''.join(filter(str.isdigit, phone)))

def get_designation(years_of_experience):
    if years_of_experience < 3:
        return "System Engineer"
    elif 3 <= years_of_experience <= 5:
        return "Data Engineer"
    elif 5 < years_of_experience <= 10:
        return "Senior Data Engineer"
    return "Lead"

def process_employee_data(data):
    processed_data = []

    for emp in data:
        try:
            processed_data.append({
                "Full Name": f"{emp['first_name']} {emp['last_name']}",
                "email": emp["email"],
                "phone": clean_phone_number(emp["phone"]),
                "gender": emp["gender"],
                "age": int(emp["age"]),
                "job_title": emp["job_title"],
                "years_of_experience": int(emp["years_of_experience"]),
                "salary": int(emp["salary"]),
                "department": emp["department"],
                "designation": get_designation(int(emp["years_of_experience"]))
            })
        except KeyError as e:
            print(f"Missing key {e} in record {emp}. Skipping entry.")
        except ValueError as e:
            print(f"Invalid value encountered: {e}. Skipping entry.")

    return pd.DataFrame(processed_data)

if __name__ == "__main__":
    raw_data = read_json_file(FILE_PATH)
    if raw_data:
        df = process_employee_data(raw_data)
        df.to_csv("employees_cleaned.csv", index=False)
        print("Processed data saved to employees_cleaned.csv")
