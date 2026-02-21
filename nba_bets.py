from nba_data import nba_data
import json

def main():
    try:
        # Load the settings from the JSON configuration file
        with open('./json/settings.json') as f:
            settings = json.loads(f.read())

        # Extract the output directory for CSV files
        csv_output_directory = settings.get('csv_output_directory')
        if not csv_output_directory:
            raise KeyError("Missing 'csv_output_directory' in settings.json")

        # Execute the NBA data workflow
        print("Starting NBA data processing...")
        nba_data(csv_output_directory)
        print(f"Data successfully exported to {csv_output_directory}")

    except FileNotFoundError:
        print("Error: 'settings.json' file not found. Please ensure the file exists in the './json/' directory.")
    except json.JSONDecodeError:
        print("Error: 'settings.json' contains invalid JSON. Please check the file for syntax errors.")
    except KeyError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()