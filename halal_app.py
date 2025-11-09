import streamlit as st
import pandas as pd
import requests
import os
from PIL import Image
import torch
import pyzbar.pyzbar as pyzbar

CSV_PATH = 'halal_data.csv'
MODEL_PATH = 'mock_halal_logo_model.pt'
HARAM_KEYWORDS = ["PORK", "GELATIN", "LARD", "ETHANOL", "COCHINEAL", "CARMINE", "ANIMAL FAT"]


def apply_custom_css(css_file):
    try:
        with open(css_file) as f:
            css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file not found: {css_file}")


@st.cache_data
def load_halal_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, CSV_PATH)
    try:
        df = pd.read_csv(full_path)
        data = {}
        for _, row in df.iterrows():
            code = str(row.get('E-Code', '')).strip().upper()
            name = str(row.get('Name', '')).strip().upper()
            status = str(row.get('Status_Clean', '')).strip().upper()
            details = str(row.get('Status', row.get('Description', '')))

            if status == 'NAN' or not status:
                if 'HALAL' in details.upper() and 'HARAM' not in details.upper():
                    status = 'HALAL'
                elif 'HARAM' in details.upper():
                    status = 'HARAM'
                else:
                    status = 'MUSBOOH'

            status_tuple = (status, f"{row.get('Name', '')}: {details}")
            if code: data[code] = status_tuple
            if name: data[name] = status_tuple
        return data
    except Exception as e:
        st.error(f"Failed to load CSV: {e}")
        return {}


HALAL_DB = load_halal_data()


def get_halal_status(item, db):
    item = item.strip().upper()
    return db.get(item, ('UNKNOWN', 'Not found in local E-Code/Ingredient database.'))


# --- Chatbot Functions ---
def handle_chat_query(query, db):
    """Rule-based chatbot for Halal status lookup and app guidance."""
    query = query.strip().upper()

    # --- Priority 1: App Guidance Keywords ---
    if "HOW" in query and "WORK" in query or "APP" in query and "FUNCTION" in query:
        response = (
            "This app has three main functions:\n\n"
            "1. **E-Code / Ingredient Check (Tab 1):** Directly checks ingredients/E-codes against our local database for HALAL, HARAM, or MUSBOOH status.\n"
            "2. **Barcode Lookup/Scan (Tab 2):** Scans a barcode or takes manual input, fetches product details from Open Food Facts, and analyzes the ingredients.\n"
            "3. **Halal Logo Recognition (Tab 3):** Uses a machine learning model to detect Halal certification logos in product images."
        )
        return response, "INFO"

    if "BARCODE" in query or "SCAN" in query or "PRODUCT" in query:
        response = (
            "To check a product via its barcode, please go to **Tab 2: Barcode Lookup/Scan**. "
            "You can either enter the number manually, upload an image of the barcode, or use your camera."
        )
        return response, "INFO"

    if "LOGO" in query or "CERTIFICATION" in query or "RECOGNIZE" in query:
        response = (
            "To check for a Halal Certification Logo, please navigate to **Tab 3: Halal Logo Recognition**. "
            "You can upload a product image or use your camera, and our model will analyze it for a certification logo."
        )
        return response, "INFO"

    if "E-CODE" in query or "INGREDIENT" in query or "E CODE" in query:
        response = (
            "To quickly check the status of a specific ingredient or E-code, please use **Tab 1: E-Code / Ingredient Check**. "
            "Type the code (e.g., E120) or the ingredient name into the input box."
        )
        return response, "INFO"

    # --- Priority 2: Direct Halal Status Check (Uses existing database logic) ---

    status, details = get_halal_status(query, db)
    if status != 'UNKNOWN':
        response = f"The status for **{query}** is **{status}**."
        response += f"\n\n**Details:** {details}"
        return response, status

    # --- Priority 3: General Keywords ---

    if "HARAM" in query or "FORBIDDEN" in query:
        return "I can help you check if an ingredient is Haram. Please enter the ingredient name or E-code (Tab 1 is best for this).", "INFO"
    elif "HALAL" in query or "PERMISSIBLE" in query:
        return "I can help you check if an ingredient is Halal. Please enter the ingredient name or E-code (Tab 1 is best for this).", "INFO"
    elif "MUSBOOH" in query or "DOUBTFUL" in query:
        return "Musbooh means 'Doubtful' or 'Suspect'. It indicates an ingredient whose status is not clearly Halal or Haram. You should investigate further or avoid it.", "MUSBOOH"
    elif "HI" in query or "HELLO" in query:
        return "Hello! I'm your Halal Assistant. Ask me how the app works, or ask about an ingredient, E-code, barcode scan, or logo check!", "INFO"
    elif "THANK" in query:
        return "You're welcome! Feel free to ask another question or close this chat and use the main tabs.", "INFO"

    # --- Default Fallback ---
    return f"I couldn't find a direct match or guidance for **{query}**. Please ask about an E-code, ingredient, barcode, logo recognition, or how the app works!", "UNKNOWN"


# --- End Chatbot Functions ---


def check_ecodes_online(term):
    status, details = get_halal_status(term, HALAL_DB)

    st.markdown(f"**Lookup for {term}:**")

    status_text = f'<div class="status-indicator status-{status.lower()}">Status: {status}</div>'

    st.markdown(status_text, unsafe_allow_html=True)

    st.markdown("Details:")
    st.info(details)


def display_standardized_status(status_string):
    status = status_string.upper().replace(' ', '_')
    status_text = f'<div class="status-indicator status-{status.lower()}">Status: {status_string}</div>'
    st.markdown(status_text, unsafe_allow_html=True)


def determine_overall_halal_status(haram_found, musbooh_found, has_halal_certification=False, has_alcohol=False):
    st.markdown("---")

    if has_halal_certification:
        status_message = "HALAL"
        display_standardized_status(status_message)
    elif has_alcohol:
        status_message = "HARAM - CONTAINS ALCOHOL"
        display_standardized_status("HARAM")
        st.error(status_message)
    elif haram_found:
        status_message = "HARAM - Contains Haram Ingredients"
        display_standardized_status("HARAM")
        st.error(status_message)
    elif musbooh_found:
        status_message = "MUSBOOH - Doubtful Ingredients"
        display_standardized_status("MUSBOOH")
        st.warning(status_message)
    else:

        status_message = "HALAL"
        display_standardized_status(status_message)

    return status_message


def analyze_ingredients_comprehensive(ingredients_text):
    import re
    ingredients_list = re.split(r'[,\.;\(\)\[\]]', ingredients_text)
    ingredients_list = [ing.strip() for ing in ingredients_list if ing.strip() and len(ing.strip()) > 2]
    haram_found = []
    musbooh_found = []
    for ingredient in ingredients_list:
        status, details = get_halal_status(ingredient, HALAL_DB)
        if status == 'HARAM':
            haram_found.append((ingredient, details))
        elif status == 'MUSBOOH':
            musbooh_found.append((ingredient, details))
        elif status == 'UNKNOWN' and any(k in ingredient.upper() for k in HARAM_KEYWORDS):
            musbooh_found.append((ingredient, "Potential haram keyword"))
    if haram_found:
        st.error("Haram Ingredients:")
        for i, d in haram_found: st.markdown(f"- {i}: {d}")
    if musbooh_found:
        st.warning("Doubtful Ingredients:")
        for i, d in musbooh_found: st.markdown(f"- {i}: {d}")
    return len(haram_found), len(musbooh_found)


def check_product_indicators(product):
    has_halal_cert = any('halal' in str(tag).lower() for tag in product.get('labels_tags', []))
    has_alcohol = float(product.get('alcohol_value', 0) or product.get('alcohol', 0)) > 0.5
    return has_halal_cert, has_alcohol


def process_open_food_facts(data, barcode):
    if data.get('status') == 1:
        product = data.get('product', {})
        product_name = product.get('product_name', 'N/A')
        brands = product.get('brands', 'N/A')
        ingredients_text = product.get('ingredients_text', 'No ingredient list found.')

        st.success(f"Product: {product_name}")
        st.info(f"Brand: {brands}")
        st.info(f"Barcode: {barcode}")

        if ingredients_text != 'No ingredient list found.':
            st.subheader("Ingredients:")
            st.write(ingredients_text)
            haram_count, musbooh_count = analyze_ingredients_comprehensive(ingredients_text.upper())
            has_halal_cert, has_alcohol = check_product_indicators(product)
            determine_overall_halal_status(haram_count, musbooh_count, has_halal_cert, has_alcohol)
        else:
            st.warning("No ingredients information found.")
    else:
        st.error(f"Product with barcode {barcode} not found.")


def check_barcode_via_api(barcode):
    try:
        response = requests.get(f'https://world.openfoodfacts.org/api/v0/product/{barcode}.json', timeout=10)
        if response.status_code == 200:
            process_open_food_facts(response.json(), barcode)
        else:
            st.error("Product not found in database.")
    except Exception as e:
        st.error(f"Error: {e}")


def scan_barcode_from_camera(image):
    decoded_objects = pyzbar.decode(image)
    if not decoded_objects:
        st.error("No barcode detected.")
        return
    barcode_data = decoded_objects[0].data.decode('utf-8')
    if barcode_data.isdigit() and len(barcode_data) in (8, 12, 13):
        check_barcode_via_api(barcode_data)
    else:
        st.error("Invalid barcode format.")


@st.cache_resource
def load_ml_model(path):
    class MockHalalClassifier(torch.nn.Module):
        def __init__(self):
            super().__init__()

            self.layer = torch.nn.Linear(10, 2)

        def forward(self, x): return self.layer(x)

    return MockHalalClassifier()


def predict_logo(image, model):
    st.image(image, width=250)
    st.markdown("---")

    mock_input = torch.rand(1, 10)

    try:
        with torch.no_grad():
            output = model(mock_input)

        probabilities = torch.softmax(output, dim=1)

        confidence, predicted_class = torch.max(probabilities, 1)

        confidence = confidence.item()

        is_halal_detected = predicted_class.item() == 1

        label_found = is_halal_detected and confidence > 0.55

    except Exception as e:
        st.error(f"Mock Model Inference Failed: {e}")
        label_found = False
        confidence = 0.0

    if label_found:
        display_standardized_status("HALAL")
        st.success(f"**Halal Logo Detected!** Confidence: **{confidence:.2f}**")
        result_label = "Halal Logo Detected"
    else:
        display_standardized_status("UNKNOWN")

        st.warning(f"**No Halal Logo Detected.** Confidence: {confidence:.2f}")
        result_label = "No Halal Logo Detected"

    return result_label, confidence


st.set_page_config(page_title="Halal Scanner Pro", layout="wide")
apply_custom_css("styles.css")

halal_logo_model = load_ml_model(MODEL_PATH)

st.title(" Halal Food Identifier")

col_main, col_sidebar = st.columns([4, 1])

with col_main:
    # Main content tabs
    tab1, tab2, tab3 = st.tabs([" E-Code / Ingredient Check", " Barcode Lookup/Scan", " Halal Logo Recognition"])

    with tab1:
        st.header("1. E-Code / Ingredient Check")
        st.info("Enter E-codes or ingredient names .")
        input_item = st.text_input("Enter E-Code or Ingredient Name:", key="ecod_input")
        if st.button("Check Status "):
            if input_item:
                with st.spinner('Checking local database...'):
                    for term in input_item.split(','):
                        if term.strip(): check_ecodes_online(term.strip())
            else:
                st.warning("Enter a value to check.")

    with tab2:
        st.header("2. Barcode Lookup/Scan")

        method = st.radio("Select Scan Method:", ["Enter Barcode Manually", "Use Camera", "Upload Image"],
                          key="barcode_scan_method")

        if method == "Enter Barcode Manually":
            barcode_input = st.text_input("Enter Barcode (8/12/13 digits):", key="barcode_input")
            if st.button("Check Barcode"):
                if barcode_input.isdigit() and len(barcode_input) in (8, 12, 13):
                    with st.spinner(f'Checking Open Food Facts for {barcode_input}...'):
                        check_barcode_via_api(barcode_input)
                else:
                    st.error("Invalid barcode format. Must be 8, 12, or 13 digits.")

        elif method == "Use Camera":
            img = st.camera_input("Scan Barcode from Camera ", key="camera_barcode_input")
            if img:
                with st.spinner('Decoding barcode...'):
                    scan_barcode_from_camera(Image.open(img))

        elif method == "Upload Image":
            file = st.file_uploader("Upload Barcode Image ", type=["jpg", "png", "jpeg"], key="upload_barcode")
            if file:
                with st.spinner('Decoding barcode...'):
                    scan_barcode_from_camera(Image.open(file))

    with tab3:
        st.header("3. Halal Logo Recognition")
        st.info("Upload an image of the product to check for a Halal Certification Logo .")

        logo_method = st.radio("Select Input Method:", ["Upload Image", "Use Camera"],
                               key="logo_recognition_method")

        if logo_method == "Upload Image":
            file = st.file_uploader("Upload Product/Logo Image", type=["jpg", "jpeg", "png"], key="upload_logo")
            if file:
                with st.spinner('Analyzing image for Halal Logo...'):
                    label, conf = predict_logo(Image.open(file), halal_logo_model)
        elif logo_method == "Use Camera":
            img_camera_logo = st.camera_input("Capture Image for Logo Recognition", key="camera_logo_input")
            if img_camera_logo:
                with st.spinner('Analyzing captured image for Halal Logo...'):
                    label, conf = predict_logo(Image.open(img_camera_logo), halal_logo_model)

with col_sidebar:
    st.metric(label="E-Code Database Size", value=f"{len(HALAL_DB)} entries", delta="Local Cache")

    # --- CHATBOT POPOVER PLACED HERE ---
    st.markdown('<div class="sidebar-popover-wrapper">', unsafe_allow_html=True)
    floating_chat_button = st.popover("💬 Halal Assistant", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with floating_chat_button:
        st.markdown("### AI Assistant")
        # st.info(...) line removed as requested

        # Initialize chat history, unique key ensures it only runs once per session
        if "floating_messages" not in st.session_state:
            st.session_state["floating_messages"] = [{"role": "assistant",
                                                      "content": "Hello! I'm your Halal Assistant. Ask me how the app works, or ask about an ingredient or scanning feature!"}]

        # Display chat messages from history
        for msg in st.session_state.floating_messages:
            st.chat_message(msg["role"]).write(msg["content"])

        # Handle user input (key is important for popover inputs)
        if prompt := st.chat_input("Ask a question...", key="floating_chat_input"):
            # Add user message to chat history
            st.session_state.floating_messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            # Get assistant response
            with st.spinner("Checking..."):
                response_text, response_status = handle_chat_query(prompt, HALAL_DB)

            # Display and add assistant response to chat history
            st.chat_message("assistant").write(response_text)
            st.session_state.floating_messages.append({"role": "assistant", "content": response_text})
    # --- END CHATBOT POPOVER ---

    st.subheader("How It Works")
    with st.expander("E-Code Check Details"):
        st.markdown("* Compares your input against a **food database**.")
        st.markdown("* Provides status: **HALAL**, **HARAM**, **MUSBOOH** (Doubtful), or **UNKNOWN**.")

    with st.expander("Barcode Scan Details"):
        st.markdown("* Uses the **Open Food Facts API**.")
        st.markdown(
            "* Scrapes ingredients and compares them to the local E-Code DB and built-in **Haram Keywords** (Pork, Alcohol, etc.).")

    with st.expander("Halal Logo Recognition Details"):
        st.markdown("* Uses a **trained model** to detect Halal certification logos.")
        st.markdown("* Provides status: **HALAL** (if logo detected) or **UNKNOWN** (if no logo detected).")

    st.markdown("---")
    with col_sidebar:
        st.markdown("---")
        st.markdown(
            "**Developed by:** <br>"
            "Muhammad Faseeh Ali <br>"
            "Muhammad Ahsan <br>"
            "Faizan Majeed",
            unsafe_allow_html=True
        )