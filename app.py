from flask import Flask, request, jsonify, send_from_directory
from lib.pdf_parser import parse_pdf

app = Flask(__name__, static_folder='.')

@app.get('/')
def root():
    return send_from_directory('.', 'index.html')

@app.post('/api/parse-pdf')
def parse_pdf_ep():
    f = request.files.get('file')
    if not f:
        return jsonify({'error': 'No file uploaded.'}), 400
    text = parse_pdf(f)
    return jsonify({'text': text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)