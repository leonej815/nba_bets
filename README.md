# NBA Data Processing and Analysis

This project automates the workflow of collecting, storing, and analyzing NBA game data. It retrieves game lines, advanced stats, and scores, processes the data, and exports it as a CSV file for further use.

## Features

- **Data Collection**: Scrapes NBA game lines, advanced stats, and scores from ESPN and NBA.com.
- **Data Storage**: Stores collected data in an SQLite database.
- **Data Export**: Exports processed data to a CSV file for analysis.
- **Prediction Criteria**: Implements various criteria for predicting game outcomes (e.g., over/under and spread picks).

## File Overview

### `nba_bets.py`
The entry point of the application. Executes the workflow by calling `nba_data` with configuration settings loaded from `settings.json`.

### `nba_data.py`
Orchestrates the workflow for:
1. Collecting pregame data (lines and stats).
2. Updating scores for completed games.
3. Exporting all data to a CSV file.

### `data_collection.py`
Contains methods for scraping:
- Game lines.
- Advanced stats (last 10 games).
- Final scores.

### `data_storage.py`
Manages the SQLite database:
- Inserts and updates game lines, stats, and scores.
- Queries for games missing specific data.

### `nba_criteria.py`
Implements logic for predicting game outcomes based on:
- Points per game (PPG).
- True shooting percentage (TS%), rebound percentage (REB%), and turnover percentage (TOV%).
- Offensive/Defensive ratings (ORtg/DRtg).

### `settings.json`
A JSON configuration file specifying the output directory for exported CSV files.

## Setup

### Prerequisites
- Python 3.7+
- Google Chrome (for Selenium WebDriver)
- Required Python packages:
  - `selenium`
  - `pytz`

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/nba-data-processing.git
   cd nba-data-processing
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Download the ChromeDriver compatible with your version of Google Chrome:
   - [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)

4. Place the `chromedriver` executable in your system's PATH or the project directory.

### Configuration
1. Create a `settings.json` file in the `json` directory:
   ```json
   {
       "csv_output_directory": "./output"
   }
   ```

2. Ensure the `json/settings.json` file specifies a valid directory for exporting CSV files.

### Database
The SQLite database is automatically created in the `sqlite` directory (`nba_bets.sqlite`) when the application runs for the first time.

## Usage

1. Run the application:
   ```bash
   python nba_bets.py
   ```

2. The script will:
   - Collect game lines, stats, and scores.
   - Update the database with the latest data.
   - Export the processed data to a CSV file.

3. Find the exported CSV file in the directory specified in `settings.json`.

## How It Works

1. **Data Collection**:
   - Scrapes game lines and stats before games begin.
   - Updates scores when games are completed.

2. **Data Storage**:
   - Stores all game data (lines, stats, scores) in a structured SQLite database.

3. **Prediction Criteria**:
   - Implements several models to predict game outcomes, such as:
     - Over/Under total line.
     - Spread picks based on stats like TS%, REB%, and TOV%.

4. **Export**:
   - Exports all data in a structured CSV format for further analysis.

## Example Output

A sample row in the exported CSV file:

| Date       | Away      | Home    | Away Spread | Home Spread | Total Line | Away Score | Home Score | TS% | REB% | TOV% | Pace |
|------------|-----------|---------|-------------|-------------|------------|------------|------------|-----|------|------|------|
| 20250510   | Lakers    | Celtics | -3.5        | 3.5         | 220.5      | 110        | 105        | 54% | 51%  | 13%  | 98   |

## Contributing

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Description of changes"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- [NBA.com](https://www.nba.com/) for stats.
- [ESPN](https://www.espn.com/) for game lines and scores.
- [Selenium](https://www.selenium.dev/) for web scraping.
