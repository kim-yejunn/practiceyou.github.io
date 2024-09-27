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

# 실행 함수
def create_app():
    app = Flask(__name__)


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

# 실행 함수
def create_app():
    app = Flask(__name__)

    
     # 세션을 사용하기 위한 비밀 키 설정
    app.secret_key = 'aa8pepole'  # 여기에 고유하고 비밀스러운 문자열을 넣으세요

    # 블루프린트 정의 및 등록을 create_app 함수 안에서 처리
    bp = Blueprint('fileupload', __name__, url_prefix='/fileupload')

    @bp.route('/result')
    def result():
        name = session.get('name')  # 세션에서 이름 가져오기
        return render_template('result.html', name=name)  # result.html에 이름 전달

    # 블루프린트를 앱에 등록
    app.register_blueprint(bp)

    @app.route('/')
    def home():
        return render_template('index.html')

    return app

# 앱 실행
if __name__ == '__main__':
    app = create_app()
    app.run('0.0.0.0', port=9005, debug=True)
