from flask import Flask, render_template, request
import os
import re
from PIL import Image
import pytesseract

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

# FIX FOR VERCEL
if not os.path.exists(UPLOAD_FOLDER):
    try:
        os.makedirs(UPLOAD_FOLDER)
    except:
        pass

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


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
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)

            try:
                file.save(filepath)
            except:
                filepath = file.filename

            image = Image.open(file)

            extracted_text = pytesseract.image_to_string(image)

            # ---------------- STORE NAME ----------------
            lines = extracted_text.split("\n")

            for line in lines:
                clean_line = line.strip()

                if len(clean_line) > 3 and clean_line.isupper():
                    store_name = clean_line
                    break

            # ---------------- DATE ----------------
            date_match = re.search(
                r"(\d{2}[/-]\d{2}[/-]\d{2,4})",
                extracted_text
            )

            if date_match:
                date = date_match.group(1)

            # ---------------- TOTAL AMOUNT ----------------
            total_match = re.search(
                r"(TOTAL|Total|total)\D+(\d+\.\d{2})",
                extracted_text
            )

            if total_match:
                total = total_match.group(2)

            # Backup total detection
            if total == "":
                all_amounts = re.findall(r"\d+\.\d{2}", extracted_text)

                if all_amounts:
                    sorted_amounts = sorted(
                        [float(x) for x in all_amounts],
                        reverse=True
                    )

                    total = str(sorted_amounts[0])

            # ---------------- CURRENCY ----------------
            if "$" in extracted_text:
                currency = "USD ($)"
            elif "RM" in extracted_text:
                currency = "MYR (RM)"
            elif "€" in extracted_text:
                currency = "EUR (€)"
            elif "£" in extracted_text:
                currency = "GBP (£)"
            else:
                currency = "Unknown"

            return render_template(
                "index.html",
                extracted_text=extracted_text,
                image_file=filepath,
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
