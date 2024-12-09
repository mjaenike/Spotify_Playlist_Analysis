# How Music Changes Throughout the Day
**How do people's listening habits change based on the time of day?**

## **Project Overview:**
This project collects data from the Spotify API on playlists; it looks to playlists with names that reference a specific time of day (e.g. 'Morning Wakeup', 'Afternoon Vibes', 'Night Chill') and explores the genres of artists in their tracklists. The project examines playlist popularity (based on followers) and the genres of artists featured in these playlists.

The goal is to uncover patterns in listening habits—whether specific genres or moods align with different times of the day. Initially, I planned to look at specific audio features of tracks; the Spotify API was narrowed to no longer include this endpoint, so I moved to exploring the genres of these playlists instead.

The findings provide insights into how music listening habits may reflect daily routines or mood changes.

## **Recreating the Python Environment**
#### Step 1: Create or Use an Existing Conda Environment
1. If you already have a Conda environment, activate it:
   ```bash
   conda activate <your_environment_name>
   ```

   Replace <your_environment_name> with the name of your existing environment.

2. If you prefer to create a new Conda environment for this project:
    ```bash
    conda create -n spotify_env python=3.12.4
    conda activate spotify_env
    ```

#### Step 2: Install Required Packages
To install the packages manually,
```bash
conda install pandas
conda install -c conda-forge dotenv
pip install requests
pip install lets-plot
```

#### Step 3: Set the .ipynb Kernel
Ensure that the Jupyter notebooks (`NB01 - Data Collection.ipynb`, `NB02 - Data Processing.ipynb`, `and NB03 - Data Visualization.ipynb`) use the same Conda environment. 

To do this:
1. **Activate Your Conda Environment**:
   - Open a terminal and activate the Conda environment:
     ```bash
     conda activate <your_environment_name>
     ```
2. **Set the Kernel in VS Code**:
   - Open your notebook in VS Code.
   - In the top-right corner of the notebook editor, look for the **Kernel Selection Dropdown**.
   - Click the dropdown and select the kernel that matches your Conda environment (e.g., `Python 3.12.4 ('spotify_env')`).

## **Obtaining Spotify API Credentials**
This project requires Spotify API credentials (Client ID and Client Secret) to authenticate and retrieve data from the Spotify API. Below are the steps to obtain and configure these credentials.

#### Step 1: Obtain Spotify API Credentials
1. Go to [Spotify for Developers](https://developer.spotify.com).
2. Log in and navigate to the **Dashboard**.
3. Create a new app by clicking "Create an App" and filling out the form.
4. Copy the **Client ID** and **Client Secret** from the app's dashboard.

#### Step 2: Save Credentials in the `.env` File
1. In the root directory of this project, create a file named `.env` (if it doesn't already exist).
2. Add the following lines to the `.env` file, replacing `your_client_id` and `your_client_secret` with the values from Spotify:
   ```plaintext
   SPOTIFY_CLIENT_ID=<your_client_id>
   SPOTIFY_CLIENT_SECRET=<your_client_secret>
   ```

**NB:** The .env file is ignored by Git using .gitignore to ensure your credentials are not shared publicly.

#### How the Credentials Are Used
The project scripts use the credentials to authenticate with the Spotify API using a custom function get_spotify_token, located in Functions.py. This function:
- Reads the SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET from the .env file.
- Generates an access token that is used for all subsequent API requests.

## **How to Run the Code**
Before running any code, ensure the following Python packages are installed and loaded:

**Required Packages:**
- `pandas`: For data manipulation and analysis.
- `sqlite3`: For database operations.
- `spotipy`: For interacting with the Spotify API.
- `dotenv`: For securely managing environment variables.
- `os`: For file system operations.
- `time`: For managing rate limits with delays.
- `lets-plot`: For data visualizations.

**Installation Instructions:**
Run the following command to install all necessary packages:
```bash
pip install pandas spotipy python-dotenv lets-plot
```

1. **Data Collection (Notebook 1):**
   - Open `code/NB01 - Data Collection.ipynb`.
   - Ensure the raw data directory (`data/raw/`) exists. If not, create it:
     ```bash
     mkdir -p data/raw
     ```
   - Execute the notebook step-by-step. This notebook:
     - Authenticates with Spotify using credentials stored in `.env`.
     - Collects playlists data related to specified time periods (e.g., morning, afternoon).
     - Saves the collected data as JSON files in the `data/raw/` directory.

Due to measures taken to avoid hitting Spotify's rate limit, the final code block of this notebook takes a long time to run (~13 mins)

2. **Data Processing (Notebook 2):**
   - Open `code/NB02 - Data Processing.ipynb`.
   - Execute the notebook to:
     - Load raw JSON files from `data/raw/`.
     - Clean and process the data into structured tables.
     - Save the processed data as a SQLite database in the `data/` directory.

3. **Data Visualization (Notebook 3):**
   - Open `code/NB03 - Data Visualization.ipynb`.
   - Execute the notebook to:
     - Load processed data from the SQLite database.
     - Create visualizations using the `lets-plot` library to answer the research question.

## **References**
For obtaining colourblind-friendly hex codes, I referred to [The Node's Data Visualization with Flying Colors](https://thenode.biologists.com/data-visualization-with-flying-colors/research/); I used the Muted qualitative color scheme.

[Tooltips](https://lets-plot.org/python/pages/tooltips.html)

**AUTHOR:** Mia Jaenike

**CANDIDATE NUMBER:** 40141

**\#TODO:**

- [ ] Add a small little image here to illustrate this project

***NB***: I was granted an extension through 20:00 December 10th, 2024.
