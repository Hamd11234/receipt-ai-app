from flask import Flask, render_template, request, send_from_directory
import pytesseract
from PIL import Image
import re
import os

app = Flask(__name__)

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads folder automatically
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route for uploaded image preview
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/', methods=['GET', 'POST'])
def index():

    extracted_text = ""
    store = ""
    date = ""
    total = ""
    currency = ""
    image_path = ""
    error_message = ""

    if request.method == 'POST':

        file = request.files['receipt']

        if file:

            # File validation
            allowed_extensions = ['png', 'jpg', 'jpeg']
            file_extension = file.filename.split('.')[-1].lower()

            if file_extension not in allowed_extensions:
                error_message = "Unsupported file type. Please upload JPG, JPEG, or PNG."

                return render_template(
                    'index.html',
                    extracted_text=extracted_text,
                    store=store,
                    date=date,
                    total=total,
                    currency=currency,
                    image_path=image_path,
                    error_message=error_message
                )

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            image_path = filepath

            try:
                image = Image.open(filepath)
            except:
                error_message = "Could not read image."

                return render_template(
                    'index.html',
                    extracted_text=extracted_text,
                    store=store,
                    date=date,
                    total=total,
                    currency=currency,
                    image_path=image_path,
                    error_message=error_message
                )

            # OCR extraction
            extracted_text = pytesseract.image_to_string(image)

            lines = extracted_text.split('\n')

            # Store name detection
            ignore_words = ["thank", "total", "cash", "change", "subtotal"]

            for line in lines:

                cleaned = line.strip()

                if (
                    cleaned
                    and len(cleaned) > 3
                    and not any(word in cleaned.lower() for word in ignore_words)
                    and not any(char.isdigit() for char in cleaned)
                ):

                    store = cleaned
                    break

            # Date detection
            date_patterns = [
                r'\d{2}/\d{2}/\d{4}',
                r'\d{2}-\d{2}-\d{4}',
                r'\d{2}/\d{2}/\d{2}',
                r'\d{1,2}/\d{1,2}/\d{2,4}'
            ]

            for pattern in date_patterns:

                date_match = re.search(pattern, extracted_text)

                if date_match:
                    date = date_match.group()
                    break

            # Total amount detection
            all_amounts = re.findall(r'\d+\.\d{2}', extracted_text)

            if all_amounts:

                numbers = [float(x) for x in all_amounts]

                total = str(max(numbers))

            # Currency detection
            if "$" in extracted_text:
                currency = "USD ($)"

            elif "RM" in extracted_text:
                currency = "MYR (RM)"

            elif "€" in extracted_text:
                currency = "EUR (€)"

            elif "£" in extracted_text:
                currency = "GBP (£)"

            else:
                currency = "USD ($)"

    return render_template(
        'index.html',
        extracted_text=extracted_text,
        store=store,
        date=date,
        total=total,
        currency=currency,
        image_path=image_path,
        error_message=error_message
    )

if __name__ == '__main__':
    app.run()
