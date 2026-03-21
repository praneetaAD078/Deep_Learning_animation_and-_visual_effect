from flask import Flask, render_template, request, url_for
import cv2
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/output'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -----------------------------
# EFFECT FUNCTIONS
# -----------------------------

def cartoonify(img_path, output_path):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    edges = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 9, 9
    )

    color = cv2.bilateralFilter(img, 9, 300, 300)
    cartoon = cv2.bitwise_and(color, color, mask=edges)

    cv2.imwrite(output_path, cartoon)


def anime_style(img_path, output_path):
    img = cv2.imread(img_path)
    anime = cv2.stylization(img, sigma_s=60, sigma_r=0.6)
    cv2.imwrite(output_path, anime)


def pixar_style(img_path, output_path):
    img = cv2.imread(img_path)
    pixar = cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)
    cv2.imwrite(output_path, pixar)


def glow_effect(img_path, output_path):
    img = cv2.imread(img_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv[:, :, 2] = cv2.add(hsv[:, :, 2], 50)
    glow = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    result = cv2.addWeighted(img, 0.6, glow, 0.4, 0)
    cv2.imwrite(output_path, result)


def gan_style(img_path, output_path):
    img = cv2.imread(img_path)
    result = cv2.stylization(img, sigma_s=150, sigma_r=0.25)
    cv2.imwrite(output_path, result)


# -----------------------------
# ROUTE
# -----------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    output_image = None
    input_image = None

    if request.method == 'POST':
        file = request.files.get('image')
        style = request.form.get('style')

        if file and file.filename != "":
            # Unique filename to avoid overwrite
            unique_name = str(uuid.uuid4()) + "_" + file.filename.replace(" ", "_")

            input_path = os.path.join(UPLOAD_FOLDER, unique_name)
            file.save(input_path)

            output_name = "output_" + unique_name
            output_path = os.path.join(OUTPUT_FOLDER, output_name)

            try:
                if style == 'cartoon':
                    cartoonify(input_path, output_path)
                elif style == 'anime':
                    anime_style(input_path, output_path)
                elif style == 'pixar':
                    pixar_style(input_path, output_path)
                elif style == 'glow':
                    glow_effect(input_path, output_path)
                elif style == 'gan':
                    gan_style(input_path, output_path)

                # Convert to URL path
                input_image = url_for('static', filename=f'uploads/{unique_name}')
                output_image = url_for('static', filename=f'output/{output_name}')

            except Exception as e:
                print("ERROR:", e)

    return render_template(
        'index.html',
        output_image=output_image,
        input_image=input_image
    )


if __name__ == '__main__':
    app.run(debug=True)