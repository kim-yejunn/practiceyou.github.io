import os, csv, tiktoken, json
from flask import Flask, render_template, request, Blueprint, send_file, redirect, url_for, session
from openai import OpenAI

# gpt api 키
name = ""
Upload_Folder = os.path.join(os.path.dirname(__file__), 'upload')
client = OpenAI(api_key= os.environ.get('api_key'))

def save_chat_history(chat_history, name):
    chat_file = os.path.join(Upload_Folder, f'{name}_chat_history.json')
    with open(chat_file, 'w', encoding='utf-8') as f:
        json.dump(chat_history, f)

def load_chat_history(name):
    chat_file = os.path.join(Upload_Folder, f'{name}_chat_history.json')
    if os.path.exists(chat_file):
        with open(chat_file, 'r', encoding='utf-8') as f:
            chat_history = json.load(f)
        return chat_history
    return []
def extraction():
    filenames = os.listdir(Upload_Folder)
    
    filepathtosave = os.path.join(Upload_Folder, 'merge.txt')
    
    with open(filepathtosave, 'w') as f:
        for filename in filenames:
            filepath = os.path.join(Upload_Folder, filename)
            with open(filepath, 'r') as file:
                data = file.read()
                f.write(data)
        
    return filepathtosave

def filter_chat(filepathtosave, name):
    if not os.path.exists(filepathtosave):
        return
    
    try:
        with open(filepathtosave, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return

    filtered_chat = []
    for line in lines:
        parts = line.strip().split(',', 2)
        if len(parts) == 3:
            _, user, message = parts
            user = user.strip('"')
            message = message.strip('"')
            if message:
                filtered_chat.append(f"{user}: {message}")

    filterfile = os.path.join(os.path.dirname(filepathtosave), 'filtered_chat.txt')
    try:
        with open(filterfile, 'w', encoding='utf-8') as file:
            file.write("\n".join(filtered_chat))
        limit_tokens_from_recent(filterfile)
    except Exception as e:
        return
    
    return filterfile

def limit_tokens_from_recent(filterfile, max_tokens=19000):
    with open(filterfile, 'r', encoding='utf-8') as file:
        data = file.read()

    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(data)

    if len(tokens) > max_tokens:
        tokens = tokens[-max_tokens:]
        data = enc.decode(tokens)

        with open(filterfile, 'w', encoding='utf-8') as file:
            file.write(data)
    
    return filterfile

def gpt_response(filterfile, name, user_message=None):
    chat_history = load_chat_history(name)
    myname = session.get('myname')

    if not chat_history:
        try:
            with open(filterfile, 'r', encoding='utf-8') as f:
                filtered_data = f.read()
        except Exception as e:
            return

        chat_history.append({
            "role": "system",
            "content": f"From now on, you are {name}. Your task is to respond exactly as {name} would in a real conversation with {myname}. \
                        Pay close attention to the tone, sentence length, typos, and even emoticons that {name} uses. The following is a reference of how {name} typically communicates:\n\n{filtered_data}"
        })

    if user_message:
        chat_history.append({
            "role": "user",
            "content": user_message
        })

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_history
        )
        gpt_reply = completion.choices[0].message.content
        chat_history.append({
            "role": "assistant",
            "content": gpt_reply
        })
        
        save_chat_history(chat_history, name)

        return gpt_reply
    except Exception as e:
        return None

# 실행 함수
def create_app():
    app = Flask(__name__)

    
     # 세션을 사용하기 위한 비밀 키 설정
    app.secret_key = 'aa8pepole'  # 여기에 고유하고 비밀스러운 문자열을 넣으세요

@bp.route('/', methods=['GET', 'POST'])
def upload_file():
    name = session.get('name')

    if os.path.exists(Upload_Folder):
        for file in os.scandir(Upload_Folder):
            os.remove(file.path)

    if request.method == 'POST':
        files = request.files.getlist('savefile')
        for file in files:
            filename = file.filename
            filepathtosave = os.path.join(Upload_Folder, filename)
            file.save(filepathtosave)
        
        merge_file_path = extraction()
        filter_chat(merge_file_path, name)
        
        return redirect(url_for('fileupload.result'))

    return render_template('submit.html', name=name)

# 블루프린트를 앱에 등록
app.register_blueprint(bp)

@bp.route('/result')
def result():
    name = session.get('name')
    return render_template('result.html', name=name)


# 앱 실행
if __name__ == '__main__':
    app = create_app()
    app.run('0.0.0.0', port=9005, debug=True)
