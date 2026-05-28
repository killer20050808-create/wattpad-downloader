import os
import requests
from flask import Flask, render_template_string, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# HTML Interface (වෙබ්සයිට් එකේ පෙනුම)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Wattpad PDF Downloader</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f9; text-align: center; padding: 50px 20px; }
        .container { max-width: 500px; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin: auto; }
        input[type="text"] { width: 100%; padding: 12px; margin: 20px 0; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        button { background: #ff6600; color: white; border: none; padding: 12px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; width: 100%; }
        button:hover { background: #e65500; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Wattpad PDF Downloader</h2>
        <p>Enter Wattpad Story ID or Link to download as PDF</p>
        <form action="/download" method="post">
            <input type="text" name="url" placeholder="https://www.wattpad.com/story/..." required>
            <button type="submit">Download PDF</button>
        </form>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', disinvestment=['POST'])
@app.route('/download', methods=['POST'])
def download():
    input_url = request.form['url']
    
    # Wattpad URL එකෙන් Story ID එක වෙන් කර ගැනීම
    try:
        story_id = input_url.split('/story/')[1].split('-')[0]
    except:
        return "වැරදි ලින්ක් එකක්! කරුණාකර නිවැරදි Wattpad Story Link එකක් ලබාදෙන්න."

    # Wattpad පොදු API එකකින් දත්ත ලබා ගැනීම
    wattpad_api = f"https://www.wattpad.com/api/v4/stories/{story_id}?parts=true"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(wattpad_api, headers=headers).json()
    
    story_title = response.get('title', 'Wattpad_Story')
    parts = response.get('parts', [])
    
    pdf_filename = f"{story_title}.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story_content = []

    # කතාවේ මාතෘකාව PDF එකට එකතු කිරීම
    story_content.append(Paragraph(f"<h1>{story_title}</h1>", styles['Title']))
    story_content.append(Spacer(1, 12))

    # සෑම පරිච්ඡේදයක්ම (Chapter) කියවා PDF එකට ඇතුළත් කිරීම
    for part in parts:
        part_id = part['id']
        part_title = part['title']
        
        # පරිච්ඡේදයේ අකුරු ටික ලබා ගැනීම
        text_api = f"https://www.wattpad.com/apiv2/storytext?id={part_id}"
        text_response = requests.get(text_api, headers=headers).text
        
        story_content.append(Paragraph(f"<h2>{part_title}</h2>", styles['Heading2']))
        story_content.append(Spacer(1, 10))
        story_content.append(Paragraph(text_response, styles['BodyText']))
        story_content.append(Spacer(1, 12))

    # PDF එක Create කිරීම
    doc.build(story_content)
    
    return send_file(pdf_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
