import pdfplumber
import os
import json

"""
Uses a "shopping list": 
    The script has a pre-made list of all the fields it needs to find, like "First name", "Postcode", and "Date of birth".

Reads the PDF like a map: 
    It sees the exact location of every word on the page.

Finds the label, then grabs the answer: 
    It looks for a label from its list (e.g., "Postcode:") and then grabs the text sitting right next to it, or in some cases, directly below it.

Saves everything: 
    It collects all the answers from all the PDFs and puts them into a single, organised data file (JSON).
"""

# --- 1. CONFIGURATION ---

# Define the major headings that delineate sections in the document.
MAJOR_HEADINGS = [
    "Registration completed by",
    "Patient registration information",
    "Patient Details",
    "Additional patient details",
    "Safeguarding Flags",
    "Ethnicity",
    "Home Address",
    "Contact Preferences",
    "Place of birth",
    "Previous GP surgery",
    "Health Authority",
    "Patient previous address",
    "Nominated Pharmacy",
    "Armed forces",
    "Emergency Contact",
    "Patient health",
    "Dispensing Patient"
]

# The master configuration for all fields to be extracted.
# The "multi_line_type" key assigns a specific extraction profile.
# - "2_line": For text that wraps to a second line next to the label.
# - "3_line": For text in a separate column that can span 3 lines.
# - "value_below": For values located on the line directly underneath the label.
FIELDS_TO_EXTRACT = {
    # Registration Completed By
    "first_name": {"labels": ["First Name"], "section_header": "Registration completed by"},
    "last_name": {"labels": ["Last name"], "section_header": "Registration completed by"},
    "relationship_to_patient": {"labels": ["Declared relationship to"], "section_header": "Registration completed by"},
    "contact_telephone": {"labels": ["Contact telephone number"], "section_header": "Registration completed by"},

    # Registration Information
    "registration_ref": {"labels": ["Registration reference"], "section_header": "Patient registration information"},
    "registration_type": {"labels": ["Registration type"], "section_header": "Patient registration information"},
    "registration_date_submitted": {"labels": ["Date registration submitted"], "section_header": "Patient registration information", "multi_line_type": "2_line"},
    "pds_match_status": {"labels": ["PDS match status"], "section_header": "Patient registration information", "multi_line_type": "2_line"},
    "identity_verified": {"labels": ["Identity verification"], "section_header": "Patient registration information", "multi_line_type": "2_line"},

    # Patient Details
    "patient_title": {"labels": ["Title"], "section_header": "Patient Details"},
    "patient_last_name": {"labels": ["Last name"], "section_header": "Patient Details"},
    "patient_first_name": {"labels": ["First name"], "section_header": "Patient Details"},
    "patient_date_of_birth": {"labels": ["Date of birth"], "section_header": "Patient Details"},
    "patient_gender": {"labels": ["Gender"], "section_header": "Patient Details"},
    "patient_First_time_registering": {"labels": ["First time registering with a"], "section_header": "Patient Details"},
    "last_uk_gp_postcode": {"labels": ["Postcode with last UK GP"], "section_header": "Patient Details"},
    "nhs_number": {"labels": ["NHS number given by patient"], "section_header": "Patient Details"},

    # Safeguarding Flags
    "safeguarding_flags": {"labels": ["Safeguarding Flags"], "section_header": "Safeguarding Flags", "multi_line_type": "value_below"},

    # Ethnicity
    "ethnicity": {"labels": ["Ethnicity"], "section_header": "Ethnicity", "multi_line_type": "3_line"},

    # Home Address
    "home_address_building": {"labels": ["Building"], "section_header": "Home Address", "multi_line_type": "2_line"},
    "home_address_street": {"labels": ["Street"], "section_header": "Home Address"},
    "home_address_town": {"labels": ["Town or city"], "section_header": "Home Address"},
    "home_address_postcode": {"labels": ["Postcode"], "section_header": "Home Address"},

    # Contact Preferences
    "Home_telephone": {"labels": ["Home telephone"], "section_header": "Contact Preferences"},
    "Mobile_telephone": {"labels": ["Mobile telephone"], "section_header": "Contact Preferences"},
    "Email": {"labels": ["Email"], "section_header": "Contact Preferences"},
    "Consent_to_contact": {"labels": ["Consent to contact"], "section_header": "Contact Preferences", "multi_line_type": "2_line"},
    "Interpreter_required": {"labels": ["Interpreter required"], "section_header": "Contact Preferences"},

    # Place of Birth
    "Country": {"labels": ["Country"], "section_header": "Place of birth"},
    "Town_or_city": {"labels": ["Town or city"], "section_header": "Place of birth"},

    # Previous GP Surgery
    "previous_gp_name": {"labels": ["Name of surgery"], "section_header": "Previous GP surgery"},
    "previous_gp_postcode": {"labels": ["Postcode"], "section_header": "Previous GP surgery"},
    "previous_gp_building": {"labels": ["Building"], "section_header": "Previous GP surgery"},
    "previous_gp_street": {"labels": ["Street"], "section_header": "Previous GP surgery"},
    "previous_gp_town": {"labels": ["Town or city"], "section_header": "Previous GP surgery"},

    # Health Authority
    "previous_health_authority": {"labels": ["Previous Health Authority"], "section_header": "Health Authority"},

    # Patient Previous Address
    "previous_home_postcode": {"labels": ["Postcode"], "section_header": "Patient previous address"},
    "previous_home_building": {"labels": ["Building"], "section_header": "Patient previous address"},
    "previous_home_street": {"labels": ["Street"], "section_header": "Patient previous address"},
    "previous_home_town": {"labels": ["Town or city"], "section_header": "Patient previous address"},

    # Nominated Pharmacy
    "pharmacy_name": {"labels": ["Name of pharmacy"], "section_header": "Nominated Pharmacy"},
    "pharmacy_building": {"labels": ["Building"], "section_header": "Nominated Pharmacy"},
    "pharmacy_town": {"labels": ["Town or city"], "section_header": "Nominated Pharmacy"},
    "pharmacy_postcode": {"labels": ["Postcode"], "section_header": "Nominated Pharmacy"},

    # Armed Forces
    "armed_forces": {"labels": ["or registered with defence"], "section_header": "Armed forces"},

    # Emergency Contact
    "emergency_contact": {"labels": ["Emergency contact"], "section_header": "Emergency Contact"},
    "emergency_contact_full_name": {"labels": ["Full name"], "section_header": "Emergency Contact"},
    "emergency_contact_relationship": {"labels": ["Relationship"], "section_header": "Emergency Contact"},
    "emergency_contact_next_of_kin": {"labels": ["Next of kin"], "section_header": "Emergency Contact"},
    "emergency_contact_telephone": {"labels": ["Contact telephone number"], "section_header": "Emergency Contact"},

    # Patient Health
    "existing_medical_conditions": {"labels": ["Existing medical conditions"], "section_header": "Patient health"},
    "medical_conditions_type": {"labels": ["Medical conditions type"], "section_header": "Patient health"},
    "medical_conditions_details": {"labels": ["Medical conditions details"], "section_header": "Patient health"},
    "allergies": {"labels": ["Allergies"], "section_header": "Patient health"},
    "mental_health_conditions": {"labels": ["Mental health conditions"], "section_header": "Patient health"},
    "disabilities": {"labels": ["Disabilities"], "section_header": "Patient health"},
    "patient_has_carer": {"labels": ["Patient has a carer"], "section_header": "Patient health"},
    "carer_type": {"labels": ["Carer type"], "section_header": "Patient health"},
    "carer_first_name": {"labels": ["First name"], "section_header": "Patient health"},
    "carer_last_name": {"labels": ["Last name"], "section_header": "Patient health"},
    "carer_relationship": {"labels": ["Relationship to patient"], "section_header": "Patient health"},
    "carer_telephone": {"labels": ["Contact telephone number"], "section_header": "Patient health"},
    "patient_is_carer": {"labels": ["Patient is a carer"], "section_header": "Patient health"},
    "patient_needs_accessibility_format": {"labels": ["Patient needs accessible"], "section_header": "Patient health"},
    "patient_needs_reasonable_adjustments": {"labels": ["Patient needs Reasonable"], "section_header": "Patient health"},
    "prescription_medication": {"labels": ["Prescription medication"], "section_header": "Patient health"},
    "prescription_details": {"labels": ["Prescription details"], "section_header": "Patient health"},
    "repeating_prescription": {"labels": ["Repeating prescription"], "section_header": "Patient health"},
    "height": {"labels": ["What is your height?"], "section_header": "Patient health"},
    "weight": {"labels": ["What is your weight?"], "section_header": "Patient health"},
    "drinks_alcohol": {"labels": ["Drinks alcohol"], "section_header": "Patient health"},
    "units_a_day": {"labels": ["Units a day"], "section_header": "Patient health"},
    "six_or_more_units": {"labels": ["Six or more units of alcohol"], "section_header": "Patient health"},
    "ever_smoked": {"labels": ["Ever smoked"], "section_header": "Patient health"},
    "smoker_type": {"labels": ["Type of smoker"], "section_header": "Patient health"},
    "Average_number_of_cigarettes": {"labels": ["Average number of cigarettes"], "section_header": "Patient health"},

    # Dispensing Patient
    "prescriptions_direct": {"labels": ["prescription items direct"], "section_header": "Dispensing Patient"},
    "live_more_than_one_mile": {"labels": ["Do you live more than 1 mile"], "section_header": "Dispensing Patient"},
    "travelling_difficulties": {"labels": ["nearest pharmacy to get"], "section_header": "Dispensing Patient"},
    "eligible_for_dispensing": {"labels": ["Eligible for dispensing"], "section_header": "Dispensing Patient"}
}

# --- 2. CORE EXTRACTION LOGIC ---

def find_value_singleline(anchor_last_word, all_words_on_page, page_width):
    """
    Finds a value strictly on the same line as its label.
    This is the default, precise method for most fields.
    """
    v_tolerance = 5
    anchor_top = anchor_last_word['top']
    anchor_bottom = anchor_last_word['bottom']
    search_x_start = anchor_last_word['x1'] + 2
    search_x_end = page_width * 0.95
    value_words = []
    for word in all_words_on_page:
        word_v_center = (word['top'] + word['bottom']) / 2
        is_vertically_aligned = (word_v_center > anchor_top - v_tolerance and word_v_center < anchor_bottom + v_tolerance)
        is_horizontally_placed = (word['x0'] > search_x_start and word['x0'] < search_x_end)
        if is_vertically_aligned and is_horizontally_placed:
            value_words.append(word)
    if value_words:
        value_words.sort(key=lambda w: w['x0'])
        full_value = " ".join(w['text'] for w in value_words)
        return full_value.strip()
    return None

def find_value_2_lines(anchor_last_word, all_words_on_page, page_width):
    """
    For fields that may wrap to a second line next to the label.
    """
    search_x_start = anchor_last_word['x1'] + 2
    search_x_end = page_width * 0.95
    search_y_start = anchor_last_word['top'] - 15 # Look up to 15px above the label
    search_y_end = anchor_last_word['bottom'] + 15
    value_words = []
    for word in all_words_on_page:
        is_horizontally_placed = word['x0'] > search_x_start and word['x0'] < search_x_end
        is_vertically_placed = word['top'] > search_y_start and word['top'] < search_y_end
        if is_horizontally_placed and is_vertically_placed:
            value_words.append(word)
    if not value_words: return None
    value_words.sort(key=lambda w: (w['top'], w['x0']))
    return " ".join(w['text'] for w in value_words).strip()

def find_value_3_lines(anchor_last_word, all_words_on_page, page_width):
    """
    For fields that may wrap to a second line next to the label.
    """
    search_x_start = page_width * 0.40 # Value is in a column starting ~40% across
    search_x_end = page_width * 0.95
    search_y_start = anchor_last_word['top'] - 20  # Look up to 20px above the label
    search_y_end = anchor_last_word['bottom'] + 60
    value_words = []
    for word in all_words_on_page:
        is_horizontally_placed = word['x0'] > search_x_start and word['x0'] < search_x_end
        is_vertically_placed = word['top'] > search_y_start and word['top'] < search_y_end
        if is_horizontally_placed and is_vertically_placed:
            value_words.append(word)
    if not value_words: return None
    value_words.sort(key=lambda w: (w['top'], w['x0']))
    return " ".join(w['text'] for w in value_words).strip()

def find_value_below(anchor_first_word, anchor_last_word, all_words_on_page):
    """
    For fields where the value is on the line(s) directly below the label.
    e.g. Safeguarding Flags
         None
    """
    # Define the search area: directly below the anchor words.
    search_y_start = anchor_last_word['bottom'] + 1  # Start immediately below the label
    search_y_end = anchor_last_word['bottom'] + 40   # Search a vertical space of ~40px
    search_x_start = anchor_first_word['x0'] - 10   # Start slightly left of the label
    search_x_end = anchor_last_word['x1'] + 100     # End to the right of the label, allowing for wider values

    value_words = []
    for word in all_words_on_page:
        # Check if the word is vertically below the anchor
        is_vertically_placed = word['top'] > search_y_start and word['top'] < search_y_end
        # Check if the word is horizontally aligned with the anchor
        is_horizontally_placed = word['x0'] > search_x_start and word['x0'] < search_x_end
        
        if is_vertically_placed and is_horizontally_placed:
            value_words.append(word)
            
    if not value_words:
        return None
        
    # Sort words by their vertical position first, then horizontal, to handle multi-line values correctly
    value_words.sort(key=lambda w: (w['top'], w['x0']))
    return " ".join(w['text'] for w in value_words).strip()


# --- 3. MAIN EXTRACTION FUNCTION ---
def extract_data_from_pdf_v3(pdf_path, master_config):
    print(f"\n--- Processing file: {os.path.basename(pdf_path)} ---")
    
    extracted_data = {header: {} for header in MAJOR_HEADINGS}

    label_to_key_map = {}
    for key, config in master_config.items():
        for label_text in config["labels"]:
            if label_text not in label_to_key_map:
                label_to_key_map[label_text] = []
            label_to_key_map[label_text].append(key)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            current_section_header = None
            
            for page_num, page in enumerate(pdf.pages):
                page_words = page.extract_words(x_tolerance=2, y_tolerance=2)
                if not page_words: continue

                i = 0
                while i < len(page_words):
                    
                    # First, check for a new major heading to set the current section context.
                    found_new_section = False
                    for header in MAJOR_HEADINGS:
                        header_parts = header.split()
                        if len(page_words) >= i + len(header_parts):
                            sequence = " ".join(w['text'] for w in page_words[i:i+len(header_parts)])
                            if sequence.strip() == header:
                                current_section_header = header
                                
                                # If the heading is also a label (Ethnicity),
                                # set the context but DON'T advance the pointer.
                                # Let the code fall through to the label check below.
                                if header == "Ethnicity" or header == "Safeguarding Flags":
                                    break
                                
                                # For all other normal headings, advance the pointer
                                # and flag that we need to skip to the next word.
                                i += len(header_parts)
                                found_new_section = True
                                break
                    
                    if found_new_section:
                        continue

                    # Second, check for a field label to extract its value.
                    found_label = False
                    for label_text, field_keys in label_to_key_map.items():
                        label_parts = label_text.split()
                        if len(page_words) >= i + len(label_parts):
                            sequence = " ".join(w['text'] for w in page_words[i:i+len(label_parts)])
                            if sequence.strip() == label_text:
                                for key in field_keys:
                                    field_config = master_config[key]
                                    field_section = field_config.get("section_header")
                                    
                                    if field_section and field_section == current_section_header:
                                        
                                        multi_line_type = field_config.get("multi_line_type")

                                        if multi_line_type == "value_below":
                                            anchor_first_word = page_words[i]
                                            anchor_last_word = page_words[i + len(label_parts) - 1]
                                            value = find_value_below(anchor_first_word, anchor_last_word, page_words)
                                        elif multi_line_type == "3_line":
                                            anchor_last_word = page_words[i + len(label_parts) - 1]
                                            value = find_value_3_lines(anchor_last_word, page_words, page.width)
                                        elif multi_line_type == "2_line":
                                            anchor_last_word = page_words[i + len(label_parts) - 1]
                                            value = find_value_2_lines(anchor_last_word, page_words, page.width)
                                        else:
                                            anchor_last_word = page_words[i + len(label_parts) - 1]
                                            value = find_value_singleline(anchor_last_word, page_words, page.width)
                                        
                                        if value:
                                            if extracted_data[field_section].get(key) is None:
                                                extracted_data[field_section][key] = value.replace("\n", " ")
                                            
                                            # Advance pointer past the label's words
                                            i += len(label_parts) 
                                            found_label = True
                                            break # break from the inner 'for key in field_keys' loop
                                if found_label: break # break from the outer 'for label_text' loop
                    
                    if found_label:
                        continue # If we found and processed a label, start the while loop again
                    
                    # If nothing was found at this position, move to the next word.
                    i += 1
    
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None

    cleaned_data = {section: fields for section, fields in extracted_data.items() if fields}
    
    return cleaned_data


# --- 4. MAIN EXECUTION ---
def main():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = os.getcwd()

    pdf_directory = os.path.join(script_dir, "pdf_documents")

    if not os.path.isdir(pdf_directory):
        print(f"Error: The directory '{pdf_directory}' was not found.")
        print("Please create a subdirectory named 'pdf_documents' in the same folder as the script and place your PDF files inside it.")
        return

    all_results = []
    print(f"Searching for PDF files in: {pdf_directory}")
    for filename in sorted(os.listdir(pdf_directory)):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, filename)
            data = extract_data_from_pdf_v3(pdf_path, FIELDS_TO_EXTRACT)
            if data:
                all_results.append({
                    "source_file": filename,
                    "extracted_data": data
                })

    if not all_results:
        print("\nNo PDF files were found or successfully processed in the directory.")
        return

    print("\n\n--- EXTRACTION COMPLETE ---")

    output_filename = "extracted_output.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults from {len(all_results)} PDF(s) have been saved to '{output_filename}' in the main script directory.")


if __name__ == "__main__":
    main()