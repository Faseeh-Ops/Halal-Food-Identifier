Halal Food Identifier

Overview:

The Halal Food Identifier is a dedicated Streamlit application designed to help users quickly and reliably check the Islamic dietary status of food products. It combines local data analysis with external APIs to provide clear, standardized results across multiple input methods.

This project is deployed and runs publicly on the Streamlit platform.

Key Features:

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

Tech Stack & Dependencies:

Framework: Streamlit

Language: Python

APIs: Open Food Facts

Libraries: streamlit, pandas, requests, pillow, torch (for mock ML), pyzbar (for barcode decoding)

Local Installation and Setup:

To run this application on your local machine, follow these steps:

1. Prerequisites

You need Python (3.8+) installed. Ensure you have the following data/config files in your root directory:

halal_data.csv (The E-code database)

mock_halal_logo_model.pt (The CV model trained on halal logos)

styles.css (The custom CSS file)

2. Setup Virtual Environment

python -m venv .venv
source .venv/bin/activate  # On macOS/Linux/Git Bash
.venv\Scripts\activate      # On Windows CMD/PowerShell


3. Install Python Dependencies

Create a requirements.txt file (if you don't have one) and install the packages:

pip install streamlit pandas requests pillow torch pyzbar


4. Running the Application

streamlit run halal_app.py


Deployment on Streamlit Cloud

The application is deployed to Streamlit Cloud, which requires two additional configuration files to run correctly due to the use of pyzbar.

Configuration Files Required

requirements.txt: Lists the Python libraries (already covered).

packages.txt: CRITICAL for installing the native ZBar dependency required by pyzbar on the Linux host environment.

File Content (packages.txt):

libzbar0


Developed by:

Muhammad Faseeh Ali

Muhammad Ahsan

Faizan Majeed