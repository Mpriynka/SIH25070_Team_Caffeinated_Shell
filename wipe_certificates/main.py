import os
import uuid
import json
import sys
from wipe_certificates.pdf_generator import generate_pdf
from wipe_certificates.pdf_signer import sign_pdf
from wipe_certificates.create_p12 import create_p12
from dotenv import load_dotenv

load_dotenv()

# --- Handle JSON input ---
if len(sys.argv) > 1:
    INPUT_JSON = sys.argv[1]  # take JSON file from command line
else:
    INPUT_JSON = "input.json"  # fallback default
print(f"Using JSON input file: {INPUT_JSON}")


P12_FILE = os.getenv("P12_FILE", "certificate.p12")
P12_PASSWORD = os.getenv("P12_PASSWORD", "123")


JSON_FOLDER = "json_reports"
PDF_FOLDER = "pdf_reports"
os.makedirs(JSON_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

def richa(data, report_uuid):
    print("=== PDF GENERATION AND SIGNING SCRIPT ===")

    # Create P12 certificate if it doesn't exist
    if not os.path.exists(P12_FILE):
        print("\n[0] Creating P12 certificate...")
        create_p12(P12_FILE, P12_PASSWORD)
        print(f"✓ Certificate created: {P12_FILE}")
    else:
        print(f"\n[0] Certificate already exists: {P12_FILE}, skipping creation")

    # print("\n[1] Loading JSON data...")
    # with open(INPUT_JSON, "r", encoding="utf-8") as f:
    #     data = json.load(f)
    # print("✓ JSON loaded successfully")

    data["report_uuid"] = report_uuid

    json_filename = os.path.join(JSON_FOLDER, f"sanitization_report_{report_uuid}.json")
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"✓ JSON saved with UUID: {json_filename}")

   
    pdf_filename = os.path.join(PDF_FOLDER, f"unsigned_report_{report_uuid}.pdf")
    print("\n[2] Generating PDF...")
    generate_pdf(data, filename=pdf_filename)
    print(f"✓ PDF generated: {pdf_filename}")

    print("\n[3] Signing PDF...")
    signed_pdf_path = os.path.join(PDF_FOLDER, f"sanitization_report_{report_uuid}.pdf")
    sign_pdf(input_pdf=pdf_filename, output_pdf=signed_pdf_path, p12_file=P12_FILE, password=P12_PASSWORD)

    if os.path.exists(signed_pdf_path):
        os.remove(pdf_filename)
        print(f"✓ Unsigned PDF deleted: {pdf_filename}")

    print(f"✓ PDF signed successfully: {signed_pdf_path}")

