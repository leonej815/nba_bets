from nba_data import nba_data
import json

def main():
    """
    Main function to execute the NBA betting data workflow.

    This script orchestrates the collection, storage, and exporting of NBA game data
    into a CSV file. It reads configuration settings from a JSON file and then uses
    the `nba_data` function to execute the workflow.

    The main steps include:
    1. Reading the output directory for the CSV file from the `settings.json` file.
    2. Passing the output directory to the `nba_data` function to process and export data.

    Raises:
        FileNotFoundError: If the `settings.json` file is not found.
        KeyError: If `csv_output_directory` is missing in the JSON configuration.
        JSONDecodeError: If the `settings.json` file contains invalid JSON.
    """
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