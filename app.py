from flask import Flask, render_template, request
import re
import os
from PIL import Image
import pytesseract

# Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():

    extracted_text = ""
    store_name = ""
    date = ""
    total = ""
    currency = ""

    if request.method == "POST":

        file = request.files["receipt"]

        if file:

            upload_folder = "static"
            os.makedirs(upload_folder, exist_ok=True)

            image_path = os.path.join(upload_folder, file.filename)

            file.save(image_path)

            image = Image.open(image_path)

            # OCR
            extracted_text = pytesseract.image_to_string(image)

            # Split lines
            lines = extracted_text.split("\n")

            # ---------------- STORE NAME ----------------
            store_name = "Unknown Store"

            for line in lines:

                clean = line.strip()

                if len(clean) > 3:

                    # Skip useless lines
                    if any(word in clean.upper() for word in [
                        "TOTAL",
                        "CASH",
                        "CHANGE",
                        "DATE",
                        "TIME",
                        "USD",
                        "AMOUNT"
                    ]):
                        continue

                    # First meaningful line becomes store name
                    store_name = clean
                    break

            # Common OCR corrections
            store_name = store_name.replace("TARGE", "TARGET")
            store_name = store_name.replace("RG", "MORE")
            store_name = store_name.replace("LESS:", "LESS")

            # ---------------- DATE ----------------
            date_match = re.search(r"\d{2}/\d{2}/\d{4}", extracted_text)

            if date_match:
                date = date_match.group()

            # ---------------- TOTAL ----------------
            amounts = re.findall(r"\d+\.\d{2}", extracted_text)

            if amounts:
                total = max([float(x) for x in amounts])

            # ---------------- CURRENCY ----------------
            if "$" in extracted_text or "USD" in extracted_text:
                currency = "USD ($)"

            elif "RM" in extracted_text:
                currency = "MYR (RM)"

            elif "€" in extracted_text:
                currency = "EUR (€)"

            else:
                currency = "Unknown"

            return render_template(
                "index.html",
                extracted_text=extracted_text,
                image_file=None,
                store_name=store_name,
                date=date,
                total=total,
                currency=currency
            )

    return render_template(
        "index.html",
        extracted_text=extracted_text,
        image_file=None,
        store_name=store_name,
        date=date,
        total=total,
        currency=currency
    )

if __name__ == "__main__":
    app.run(debug=True)
