Halal Food Identifier 

Overview

The Halal Food Identifier is a dedicated Streamlit application designed to help users quickly and reliably check the Islamic dietary status of food products. It combines local data analysis with external APIs to provide clear, standardized results across multiple input methods.

This project is deployed and runs publicly on the Streamlit platform.

Key Features

The application is organized into three main functional tabs:

E-Code / Ingredient Check

Provides instant HALAL, HARAM, MUSBOOH (Doubtful), or UNKNOWN status by checking E-codes or ingredient names against a local database.

Barcode Lookup/Scan

Allows input via manual entry, image upload, or live camera scan.

Integrates with the Open Food Facts API to fetch comprehensive ingredient lists.

Analyzes ingredients against a list of Haram keywords and the local E-Code database.

Halal Logo Recognition

Uses a camera or image upload to check for the presence of Halal certification logos via a mock Machine Learning model.

Standardizes status output to HALAL (if detected) or UNKNOWN (if not detected).
<img width="3840" height="1650" alt="image" src="https://github.com/user-attachments/assets/91e3c6c3-ef21-4719-a51b-839fea03ff4e" />
<img width="3840" height="1656" alt="image" src="https://github.com/user-attachments/assets/f2f341dc-93fc-48ec-a72d-731026526d82" />
<img width="3840" height="1647" alt="image" src="https://github.com/user-attachments/assets/c0f6deef-a622-4000-b5fa-c2e8557b64f9" />


Tech Stack

Framework: Streamlit

Language: Python

Styling: Custom CSS injected into Streamlit

Libraries: streamlit, pandas, requests, pillow, torch (for mock ML), pyzbar (for barcode decoding)

How to Run Locally

Follow these steps to get the application running on your local machine.

Clone the Repository

git clone [https://github.com/your-username/your-repository-name.git](https://github.com/Faseeh-Ops/Halal-Food-Identifier)
cd your-repository-name



Create and Activate a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

For Windows:

python -m venv venv 
.\venv\Scripts\activate


For macOS/Linux:

python3 -m venv venv 
source venv/bin/activate


Install Dependencies

Install all the required libraries from the requirements.txt file.

pip install -r requirements.txt


Run the Streamlit App

Execute the following command in your terminal.

streamlit run halal_app.py


The application should automatically open in a new tab in your web browser!

Deployment

Deployed successfully on Streamlit:
https://halal-food-identifier.streamlit.app/

Configuration Files Required

requirements.txt: Lists the Python libraries.

packages.txt: CRITICAL for installing the native ZBar dependency (libzbar0) required by pyzbar on the Linux host environment.

File Structure

The project is organized into the following key files:

halal_app.py: The main application file. It handles the page layout, user inputs, and scanning logic.

styles.css: Contains the custom CSS for the enhanced and color-coded UI.

halal_data.csv: The local E-code and ingredient database used for lookups.

mock_halal_logo_model.pt: The mock model file for logo recognition.

requirements.txt: Lists all the Python libraries required to run the project.

packages.txt: Specifies the necessary Linux system dependency (libzbar0).
<img width="1128" height="504" alt="image" src="https://github.com/user-attachments/assets/f7aeef36-b026-49da-8f8c-0de220826b39" />


How to Upload Your Project to GitHub from PyCharm

This is a detailed, step-by-step guide if you are using the PyCharm IDE.

Step 1: Get Your Project Ready

Create .gitignore: This is a very important step to prevent uploading unnecessary files (like your virtual environment).

In the PyCharm project panel, right-click your main folder -> New -> File.
Name the file .gitignore (the dot at the beginning is crucial).

Paste the following content into it:

# Virtual Environment
venv/
.venv/

# PyCharm files
.idea/

# Python cache
__pycache__/
*.pyc


Step 2: Push to GitHub

Go to VCS (Version Control System) menu at the top.

Select Import into Version Control -> Share Project on GitHub.

Follow the prompts to name your repository and push the project.

