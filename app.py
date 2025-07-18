from flask import Flask, request, send_from_directory
import os
from spleeter.separator import Separator

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

@app.route('/')
def home():
    return '''
    <h2> Stem Wave Stem Splitter</h2>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file" accept=".mp3" required>
        <button type="submit">Upload</button>
    </form>
    '''

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file.filename.endswith('.mp3'):
        return "❌ Only .mp3 files allowed", 400

    filename = file.filename
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(upload_path)

    # Extract filename without extension
    base_name = os.path.splitext(filename)[0]
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], base_name)

    # Run Spleeter to separate stems
    separator = Separator('spleeter:2stems')
    separator.separate_to_file(upload_path, app.config['OUTPUT_FOLDER'])

    return f'''
    ✅ File uploaded and processed: {filename}<br><br>
    🔗 Download links:<br>
    <a href="/download/{base_name}/vocals.wav">⬇️ Download Vocals</a><br>
    <a href="/download/{base_name}/accompaniment.wav">⬇️ Download Music</a><br>
    '''

@app.route('/download/<song>/<stem>')
def download(song, stem):
    dir_path = os.path.join(app.config['OUTPUT_FOLDER'], song)
    return send_from_directory(dir_path, stem)

if __name__ == '__main__':
    app.run(debug=True)
