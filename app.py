import os, csv, tiktoken, json
from flask import Flask, render_template, request, Blueprint, send_file, redirect, url_for, session
from openai import OpenAI

# gpt api 키
client = OpenAI(api_key= os.environ.get('api_key'))

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
