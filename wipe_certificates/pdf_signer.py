# import os
# from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
# from pyhanko.sign.fields import SigFieldSpec, append_signature_field
# from pyhanko.sign.signers.pdf_signer import PdfSigner, PdfSignatureMetadata
# from pyhanko.sign.signers.pdf_cms import SimpleSigner
# from pyhanko.sign.fields import VisibleSigSettings

# # --- Configuration ---
# P12_FILE_PATH = "certificate.p12"
# PASSWORD = os.getenv("PDF_SIG_PASSWORD", "123")
# INPUT_PDF = "sanitization_report.pdf"
# OUTPUT_PDF = "agreement_signed.pdf"

# def sign_pdf(input_pdf=INPUT_PDF, p12_file=P12_FILE_PATH, password=PASSWORD):
#     """
#     Load a P12 certificate, sign the PDF, and save the output.
#     Signature will be placed on the last page.
#     """
#     try:
#         # Load signer from the .p12 file
#         signer = SimpleSigner.load_pkcs12(
#             p12_file,
#             passphrase=password.encode("utf-8")
#         )

#         # Open input PDF and prepare writer
#         with open(input_pdf, "rb") as doc:
#             writer = IncrementalPdfFileWriter(doc)

#             # Get last page index
#             last_page_index = writer.root['/Pages']['/Count'] - 1

#             # Define visible signature field on last page
#             append_signature_field(
#                 writer,
#                 SigFieldSpec(
#                     sig_field_name="Signature1",
#                     on_page=last_page_index,  # updated parameter name
#                     box=(50, 50, 250, 100),  # bottom-left corner box
#                     visible_sig_settings=VisibleSigSettings(
#                         rotate_with_page=True,
#                         scale_with_page_zoom=True,
#                         print_signature=True
#                     )
#                 )
#             )

#             # Create metadata for signature
#             meta = PdfSignatureMetadata(field_name="Signature1")

#             # Sign and save the output PDF
#             pdf_signer = PdfSigner(meta, signer=signer)
#             with open(OUTPUT_PDF, "wb") as out:
#                 pdf_signer.sign_pdf(writer, output=out)

#         print(f"✅ Successfully signed '{input_pdf}' → '{OUTPUT_PDF}'")
#         return OUTPUT_PDF

#     except Exception as e:
#         print(f"❌ Error signing PDF: {e}")
#         return None

# pdf_signer.py
import os
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign.fields import SigFieldSpec, append_signature_field, VisibleSigSettings
from pyhanko.sign.signers.pdf_signer import PdfSigner, PdfSignatureMetadata
from pyhanko.sign.signers.pdf_cms import SimpleSigner

def sign_pdf(input_pdf, output_pdf, p12_file, password):
    """
    Load a P12 certificate, sign the PDF, and save the output.
    Signature will be placed on the last page.
    """
    try:
        # Load signer from the .p12 file
        signer = SimpleSigner.load_pkcs12(
            p12_file,
            passphrase=password.encode("utf-8")
        )

        # Open input PDF and prepare writer
        with open(input_pdf, "rb") as doc:
            writer = IncrementalPdfFileWriter(doc)

            # Get last page index
            last_page_index = writer.root['/Pages']['/Count'] - 1

            # Define visible signature field on last page
            append_signature_field(
                writer,
                SigFieldSpec(
                    sig_field_name="Signature1",
                    on_page=last_page_index,  # last page
                    box=(50, 50, 250, 100),   # bottom-left corner box
                    visible_sig_settings=VisibleSigSettings(
                        rotate_with_page=True,
                        scale_with_page_zoom=True,
                        print_signature=True
                    )
                )
            )

            # Create metadata for signature
            meta = PdfSignatureMetadata(field_name="Signature1")

            # Sign and save the output PDF
            pdf_signer = PdfSigner(meta, signer=signer)
            with open(output_pdf, "wb") as out:
                pdf_signer.sign_pdf(writer, output=out)

        print(f"✅ Successfully signed '{input_pdf}' → '{output_pdf}'")
        return output_pdf

    except Exception as e:
        print(f"❌ Error signing PDF: {e}")
        return None
