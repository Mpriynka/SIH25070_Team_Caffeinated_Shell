import json
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from wipe_certificates.main import richa

class CertificateGenerator:
    """Generates PDF and JSON certificates of sanitization."""

    def __init__(self, user_data, system_data, wiped_devices, wipe_report, certificate_id):
        self.user_data = user_data
        self.system_data = system_data
        self.wiped_devices = wiped_devices # Add this
        self.wipe_report = wipe_report
        self.certificate_id = certificate_id
        self.timestamp = datetime.utcnow()

    def _create_data_dict(self):
        """Creates a comprehensive dictionary for the certificate."""

        return {
        "personPerformingSanitization": {
            "name": self.user_data.get("name"),
            "title": self.user_data.get("title"),
            "organization": self.user_data.get("organization"),
            "location": self.user_data.get("location"),
            "phone": self.user_data.get("phone"),
        },
        
        "mediaInformation": {
            "makeVendor": self.system_data.get("system_details", {}).get("vendor"),
            "modelNumber": self.system_data.get("system_details", {}).get("model"),
            "serialNumber": ' '.join([dev.get("serial", "N/A") for dev in self.wiped_devices]),
            "mediaPropertyNumber": self.user_data.get("media_property_number"),
            "mediaType": "-",
            "source": self.user_data.get("source"),
            "classification": "Not Applicable",
            "dataBackedUp": str(bool(self.user_data.get("backup_location"))),
            "backupLocation": self.user_data.get("backup_location"),
        },
        
        "sanitizationDetails": {
            "methodType": "Purge",
            "methodUsed": self.wipe_report.get("method_used"),
            "methodDetails": "-",
            "toolUsed": "Secure Data Wiper v1.0",
            "verificationMethod": "Not performed in this version",
            "postSanitizationClassification": "Unclassified",
            "notes": self.user_data.get("notes"),
        },
        
        "mediaDestination": {
            "destination": "-",
            "details": self.user_data.get("destination"),
        },
        
        "validation": {
            "validatorName": "-",
            "validatorTitle": "-",
            "validatorOrganization": "-",
            "validatorLocation": "-",
            "validatorPhone": "-",
            "validationDate": "-"
        }
    }

    def generate_pdf(self):
        """Generates a PDF certificate file using ReportLab."""
        data = self._create_data_dict()
        richa(data, self.certificate_id)
        