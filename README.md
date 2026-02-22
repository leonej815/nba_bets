# NBA Bets Data Pipeline

This project automates the collection, processing, storage, and export of NBA game and betting data for analytics and betting strategies. Data is scraped, processed, stored, and exported to CSV format for your use. The repository is maintained by Joseph Leone.

## Features
- Scrapes pregame betting lines, team stats, and final NBA scores
- Stores all data in a local SQLite database
- Outputs CSV files for easy access and further analysis
- Modular design with clear separation between collection and storage

## Project Structure
- `main.py` – Entry point: coordinates setup and workflow
- `data_collection.py` – Handles web scraping via Selenium
- `data_storage.py` – Handles SQLite storage and queries
- `nba_data.py` – Defines NBA data processing workflow
- `/json/settings.json` – Configuration file specifying CSV output directory
- `/sqlite/nba_bets.sqlite` – Main database

## Getting Started
1. **Install Dependencies**
   - Python ≥ 3.7
   - `selenium`, `pytz`, `sqlite3`
2. **Configure Settings**
   - Ensure `settings.json` is present in `/json/`
   - Set your desired CSV output directory in `settings.json`
3. **Run the Pipeline**
   ```bash
   python main.py
   ```
   - First run will create a config file from `settings.template.json` if missing.

## Workflow Outline
- Loads configuration from JSON
- Scrapes betting lines, stats, scores
- Stores new games and stats (insert/update logic)
- Finds games without scores and fills them in
- Exports all game data to CSV

## Data Details
- **Betting Lines**: Scraped from ESPN on game day
- **Stats**: Pulled from NBA.com (last 10 games, advanced stats)
- **Scores**: Fetched postgame from ESPN
- **Storage**: Each game record includes teams, lines, stats, scores (see `nba_game_data` schema in SQLite)

## Customization & Extension
- Add new stats or lines by expanding `Data_Collection` methods
- Change database schema by editing `Data_Storage`
- Update CSV export destinations via `settings.json`

## Troubleshooting
- Missing `settings.json`: Will auto-create from template if available
- Invalid JSON in config: Error message guides fixes
- Database or scraping issues: Check dependencies, site layout changes

## Credits
Created by Joseph Leone.

---
**Note:** This pipeline uses Selenium for web scraping. Ensure that ChromeDriver is installed and compatible with your local Chrome version.