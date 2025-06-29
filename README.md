Advanced UFC Tracker 🥋
This is a web application project that allows you to search for detailed information about UFC fighters and view upcoming events. It uses web scraping to obtain updated data directly from the official UFC statistics website.

Features
Fighter Search: Search for fighters by name.

Fighter Details: Displays the fighter's record, height, weight, reach, and actual weight class.

Social Media Links: Provides direct links to the fighter's Twitter and Instagram profiles (if available).

Upcoming Events: Lists upcoming UFC events with their dates and featured fights.

Category Organization: Fighter search results are organized by their weight class.

Technologies Used
Python: Main programming language.

Flask: Web microframework for Python.

Requests: HTTP library for making web requests.

BeautifulSoup4 (bs4): Library for parsing HTML and XML (web scraping).

HTML/CSS: For the user interface structure and styling.

Setup and Execution
Follow these steps to set up and run the project on your local machine:

1. Clone the Repository (If you haven't already)
If you already have the files locally, you can skip this step. If you are getting the project from a Git repository, clone it:

git clone [https://github.com/franbucho/UFCTrack.git](https://github.com/franbucho/UFCTrack.git)
cd UFCTrack

2. Create a Virtual Environment (Recommended)
It's good practice to create a virtual environment to manage project dependencies.

python -m venv venv

3. Activate the Virtual Environment
On Windows:

.\venv\Scripts\activate

On macOS/Linux:

source venv/bin/activate

4. Install Dependencies
With the virtual environment activated, install the necessary libraries:

pip install Flask requests beautifulsoup4

5. File Structure
Ensure your files are organized as follows:

ufcTrack/
├── app.py
└── templates/
    └── index.html

6. Run the Flask Application
From the ufcTrack directory, with the virtual environment activated, run the application:

python app.py

7. Access the Application
Open your web browser and visit:

[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

You should now be able to use the UFC Tracker!

Important Notes on Web Scraping
Performance: Searching for fighters involves scanning the UFC Stats website by alphabet letters. This can take time, especially if the connection is slow or the site is under heavy load.

Reliability: Web scraping is sensitive to changes in the structure of the ufcstats.com website. If the site changes its HTML, the scraping logic in app.py might need to be updated to continue extracting data correctly.

Terms of Service: Make sure to review the terms of service for ufcstats.com before performing large-scale scraping or for commercial purposes.
