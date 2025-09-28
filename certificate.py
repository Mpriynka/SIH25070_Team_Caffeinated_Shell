import json
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

class CertificateGenerator:
    """Generates PDF and JSON certificates of sanitization."""

    def __init__(self, user_data, system_data, wipe_report, certificate_id):
        self.user_data = user_data
        self.system_data = system_data
        self.wipe_report = wipe_report
        self.certificate_id = certificate_id
        self.timestamp = datetime.utcnow()

    def _create_data_dict(self):
        """Creates a comprehensive dictionary for the certificate."""
        return {
            "certificate_id": self.certificate_id,
            "certificate_timestamp_utc": self.timestamp.isoformat() + "Z",
            "person_performing_sanitization": {
                "name": self.user_data.get("name"),
                "organization": self.user_data.get("organization"),
                "title": self.user_data.get("title"),
                "location": self.user_data.get("location"),
                "phone": self.user_data.get("phone"),
            },
            "media_information": {
                "make_vendor": self.system_data.get("system_details", {}).get("vendor"),
                "model_number": self.system_data.get("system_details", {}).get("model"),
                "serial_numbers": [dev.get("serial", "N/A") for dev in self.system_data.get("storage_devices", [])],
                "media_property_number": self.user_data.get("media_property_number"),
                "source": self.user_data.get("source"),
                "backup_location": self.user_data.get("backup_location"),
            },
            "sanitization_details": {
                "method_type": "Purge",
                "method_used": self.wipe_report.get("method_used"),
                "tool_used": "Secure Data Wiper v1.0",
                "verification_method": "Not performed in this version",
                "notes": self.user_data.get("notes"),
            },
            "media_destination": {
                "details": self.user_data.get("destination")
            },
            "wipe_process_report": self.wipe_report
        }

    def generate_json(self):
        """Generates a JSON certificate file."""
        data = self._create_data_dict()
        filename = f"{self.certificate_id}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"JSON certificate saved to {filename}")

    def generate_pdf(self):
        """Generates a PDF certificate file using ReportLab."""
        data = self._create_data_dict()
        filename = f"{self.certificate_id}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        def draw_header(text, y):
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(width / 2.0, y, text)
            c.line(inch, y - 0.1 * inch, width - inch, y - 0.1 * inch)
            return y - 0.3 * inch

        def draw_field(label, value, x, y, c):
            c.setFont("Helvetica-Bold", 10)
            c.drawString(x, y, f"{label}:")
            c.setFont("Helvetica", 10)
            c.drawString(x + 1.5 * inch, y, str(value))
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2.0, height - 0.5 * inch, "CERTIFICATE OF SANITIZATION")
        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2.0, height - 0.7 * inch, f"Ref. ID: {self.certificate_id}")
        
        y_pos = height - 1.2 * inch
        
        # Person Information
        y_pos = draw_header("PERSON PERFORMING SANITIZATION", y_pos)
        person = data["person_performing_sanitization"]
        draw_field("Name", person["name"], inch, y_pos, c)
        draw_field("Title", person["title"], inch * 4.5, y_pos, c)
        y_pos -= 0.25 * inch
        draw_field("Organization", person["organization"], inch, y_pos, c)
        y_pos -= 0.25 * inch
        draw_field("Location", person["location"], inch, y_pos, c)
        draw_field("Phone", person["phone"], inch * 4.5, y_pos, c)
        y_pos -= 0.3 * inch
        
        # Media Information
        y_pos = draw_header("MEDIA INFORMATION", y_pos)
        media = data["media_information"]
        draw_field("Make/Vendor", media["make_vendor"], inch, y_pos, c)
        draw_field("Model Number", media["model_number"], inch * 4.5, y_pos, c)
        y_pos -= 0.25 * inch
        draw_field("Serial Number(s)", ', '.join(media["serial_numbers"]), inch, y_pos, c)
        y_pos -= 0.25 * inch
        draw_field("Media Property No.", media["media_property_number"], inch, y_pos, c)
        y_pos -= 0.25 * inch
        draw_field("Source", media["source"], inch, y_pos, c)
        y_pos -= 0.3 * inch
        
        # Sanitization Details
        y_pos = draw_header("SANITIZATION DETAILS", y_pos)
        sanitization = data["sanitization_details"]
        wipe = data["wipe_process_report"]
        draw_field("Method Used", sanitization["method_used"], inch, y_pos, c)
        draw_field("Tool Used", sanitization["tool_used"], inch*4.5, y_pos, c)
        y_pos -= 0.25 * inch
        draw_field("Wipe Start (UTC)", wipe["start_time_utc"], inch, y_pos, c)
        draw_field("Wipe End (UTC)", wipe["end_time_utc"], inch * 4.5, y_pos, c)
        y_pos -= 0.25 * inch
        draw_field("Wipe Status", wipe["status"], inch, y_pos, c)
        y_pos -= 0.25 * inch
        draw_field("Notes", sanitization["notes"], inch, y_pos, c)
        
        c.save()
        print(f"PDF certificate saved to {filename}")

    def generate_all(self):
        """Generates both JSON and PDF files."""
        self.generate_json()
        self.generate_pdf()

if __name__ == '__main__':
    # For testing the module directly
    mock_user = { "name": "Test User", "organization": "Test Corp"}
    mock_sys = { "system_details": {"vendor": "Dell", "model": "XPS"}, "storage_devices": [{"serial": "123"}, {"serial": "456"}]}
    mock_wipe = { "status": "Success", "method_used": "Test Method" }
    
    cert = CertificateGenerator(mock_user, mock_sys, mock_wipe, "test-uuid-12345")
    cert.generate_all()