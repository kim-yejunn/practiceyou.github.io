import os, csv, tiktoken, json
from flask import Flask, render_template, request, Blueprint, send_file, redirect, url_for, session
from openai import OpenAI

# 전역 변수
name = ""
    # 현재 파일(app.py)이 있는 디렉토리 기준으로 'upload' 폴더 경로 설정
Upload_Folder = os.path.join(os.path.dirname(__file__), 'upload')
    # gpt api 키(.env 파일에 gpt api 키 저장 후 실행)
client = OpenAI(api_key= os.getenv('api_key'))

# 토큰 마지막 내용 19000개로 제한
def limit_tokens_from_recent(filterfile, max_tokens=19000):
    with open(filterfile, 'r', encoding='utf-8') as file:
        data = file.read()
    
    # GPT-4 모델에 호환되는 인코딩 사용
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(data)
    
    # 토큰이 max_tokens를 초과하는 경우, 뒤에서부터 max_tokens 만큼 남기기
    if len(tokens) > max_tokens:
        tokens = tokens[-max_tokens:]  # 뒤에서부터 max_tokens만큼 자름
        data = enc.decode(tokens)
    
        # 제한된 토큰으로 파일을 다시 저장
        with open(filterfile, 'w', encoding='utf-8') as file:
            file.write(data)
    
    print(f"최근 내용을 기준으로 토큰 제한 후 파일 저장 완료: {filterfile}")

    return filterfile

# 채팅 내용 저장 및 불러오기
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

# 업로드 된 파일 merge로 통합
def extraction():
    filenames = os.listdir(Upload_Folder)
    print(f"폴더 내 업로드 된 파일 이름: {filenames}")  # 디버깅 출력
    
    # 파일 경로 설정
    filepathtosave = os.path.join(Upload_Folder, 'merge.txt')
    
    with open(filepathtosave, 'w') as f:
        for filename in filenames:
            filepath = os.path.join(Upload_Folder, filename)
            with open(filepath, 'r') as file:
                data = file.read()
                f.write(data)
        
    return filepathtosave  # '0' 대신 병합된 파일 경로를 반환

def filter_chat(filepathtosave, name):
    # print(f"필터링 할 이름: {name}") # 필터링 둘의 대화 다 가져오기 

    # 파일 존재 여부 확인
    if not os.path.exists(filepathtosave):
        print(f"파일 존재 안 함: {filepathtosave}")
        return
    
    try:
        # 파일 읽기 시도
        with open(filepathtosave, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"파일 문장 수: {len(lines)}")
    except Exception as e:
        print(f"파일 읽기 실패: {e}")
        return

    # 디버깅: 파일 내용 출력
    print("파일 내용 출력(첫 10줄):")
    for i, line in enumerate(lines[:10]):
        print(f"Line {i+1}: {line.strip()}")

    # 필터링 과정에서 이름과 메시지만 남기기
    try:
        filtered_chat = []
        for line in lines:
            parts = line.strip().split(',', 2)  # Date, User, Message로 분리
            if len(parts) == 3:
                _, user, message = parts
                user = user.strip('"')  # 이름에서 따옴표 제거
                message = message.strip('"')  # 메시지에서 따옴표 제거
                # 필터링 조건: 메시지가 존재하고, 입력된 이름과 관계없이 대화 내용을 포함
                if message:
                    filtered_chat.append(f"{user}: {message}")
        
        print(f"필터 된 문장 수: {len(filtered_chat)}")
    except Exception as e:
        print(f"필터링 중 에러: {e}")
        return

    # 필터링된 내용 저장
    if not filtered_chat:
        print("채팅 내용을 찾을 수 없습니다.")
        return
    
    filterfile = os.path.join(os.path.dirname(filepathtosave), 'filtered_chat.txt')
    try:
        with open(filterfile, 'w', encoding='utf-8') as file:
            file.write("\n".join(filtered_chat))
        print(f"필터링 채팅 저장: {filterfile}")
        # 토큰 제한 함수 호출
        limit_tokens_from_recent(filterfile)

    except Exception as e:
        print(f"필터링 채팅 저장 에러 발생: {e}")
        return
    
    return filterfile

# gpt 응답
def gpt_response(filterfile, name, user_message=None):
    # 이전 대화 세션에서 저장된 메시지 가져오기
    chat_history = load_chat_history(name)
    myname = session.get('myname')  # 세션에서 내 이름 가져오기
    print(f"내 이름: {myname}")  # 로그 추가

    if not chat_history:
        # 첫 번째 요청일 때, 파일에서 대화 내용을 불러와서 초기 메시지를 구성
        try:
            with open(filterfile, 'r', encoding='utf-8') as f:
                filtered_data = f.read()
            print("필터링 파일 읽기 성공")
        except Exception as e:
            print(f"필터링 파일 읽기 실패: {e}")
            return

        # 초기 메시지 설정: 상대방의 대화 패턴을 철저히 모방하도록 지시
        chat_history.append({
            "role": "system",
            "content": f"From now on, you are {name}. Your task is to respond exactly as {name} would in a real conversation with {myname}. \
                        Pay close attention to the tone, sentence length, typos, and even emoticons that {name} uses. The following is a reference of how {name} typically communicates:\n\n{filtered_data}"
        })

    # 사용자 메시지가 있을 때 추가
    if user_message:
        chat_history.append({
            "role": "user",
            "content": user_message
        })

    # GPT 요청
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_history
        )
        # GPT 응답을 받아서 대화 기록에 추가
        gpt_reply = completion.choices[0].message.content
        chat_history.append({
            "role": "assistant",
            "content": gpt_reply
        })
        
        # GPT 응답 후 대화 기록을 파일에 저장
        save_chat_history(chat_history, name)

        return gpt_reply
    except Exception as e:
        print(f"Error during GPT request: {e}")
        return None

# 실행 함수
def create_app():
    app = Flask(__name__)
    
     # 세션을 사용하기 위한 비밀 키 설정
    app.secret_key = 'aa8pepole'  # 여기에 고유하고 비밀스러운 문자열을 넣으세요
    
    # upload 폴더가 없으면 생성
    if not os.path.exists(Upload_Folder):
        os.makedirs(Upload_Folder)

    # 블루프린트 정의 및 등록을 create_app 함수 안에서 처리
    bp = Blueprint('fileupload', __name__, url_prefix='/fileupload')

    @bp.route('/', methods=['GET', 'POST'])
    def upload_file():
        name = session.get('name')  # 세션에서 이름 가져오기
        print("upload_file 실행 성공")  # 로그 추가
        
        # upload 폴더에 있는 파일 삭제
        if os.path.exists(Upload_Folder):
            for file in os.scandir(Upload_Folder):
                os.remove(file.path)
            print("Upload folder 내 파일 삭제")  # 로그 추가
        
        if request.method == 'POST':
            print("POST 받음")  # 로그 추가
            
            files = request.files.getlist('savefile')  # 여러 파일을 처리하기 위해 getlist 사용
            for file in files:
                filename = file.filename
                filepathtosave = os.path.join(Upload_Folder, filename)
                file.save(filepathtosave)
                print(f"File 저장: {filename}")  # 로그 추가
            
            # 파일 업로드 후 경로 받아오기
            merge_file_path = extraction()
            print(f"Merged file 경로: {merge_file_path}")  # merge_file_path 출력

            filter_chat(merge_file_path, name)
            
            return redirect(url_for('fileupload.result'))  # 결과 페이지로 리다이렉트

        return render_template('submit.html', name=name)  # 파일 업로드 페이지를 표시할 때 이름도 전달

    @bp.route('/result')
    def result():
        name = session.get('name')  # 세션에서 이름 가져오기
        return render_template('result.html', name=name)  # result.html에 이름 전달

    # 블루프린트를 앱에 등록
    app.register_blueprint(bp)

    @app.route('/')
    def home():
        return render_template('index.html')
    
    @app.route('/myname')
    def myname():
        return render_template('myname.html')

    @app.route('/myname/submit')
    def submit_myname():
        myname = request.args.get('myname')
        session['myname'] = myname  # 세션에 내 이름 저장
        return redirect(url_for('yourname'))  # 상대방 이름 입력 페이지로 리다이렉트

    @app.route('/yourname')
    def yourname():
        return render_template('yourname.html')

    @app.route('/yourname/submit')
    def submit():
        global name
        name = request.args.get('name')
        session['name'] = name  # 세션에 이름 저장
        return redirect(url_for('fileupload.upload_file'))  # 파일 업로드 페이지로 리다이렉트

    @app.route('/send_message', methods=['POST'])
    def send_message():
        global name  # 사용자가 입력한 name을 사용
        data = request.get_json()
        user_message = data['message']

        # 파일 경로를 가져와서 GPT 응답을 생성
        merge_file_path = os.path.join(Upload_Folder, 'merge.txt')  # 병합된 파일 경로
        filter_file = filter_chat(merge_file_path, name)  # 필터링 파일 생성

        if filter_file:
            reply = gpt_response(filter_file, name, user_message)  # 수정된 함수 호출
            if reply:
                return {'reply': reply}
            else:
                return {'error': 'GPT 응답 생성 중 오류가 발생했습니다.'}
        else:
            return {'error': '필터링 파일 생성 중 오류가 발생했습니다.'}

    return app

# 앱 실행
if __name__ == '__main__':
    app = create_app()
    app.run('0.0.0.0', port=9005, debug=True)
