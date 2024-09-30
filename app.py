import os, csv, tiktoken, json, re
from flask import Flask, render_template, request, Blueprint, send_file, redirect, url_for, session
from openai import OpenAI

# 전역 변수
name = ""
Upload_Folder = os.path.join(os.path.dirname(__file__), 'upload')
client = OpenAI(api_key=os.getenv('api_key'))

# 토큰 마지막 내용 19000개로 제한
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
    print(f"폴더 내 업로드 된 파일 이름: {filenames}") 
    
    filepathtosave = os.path.join(Upload_Folder, 'merge.txt')
    
    with open(filepathtosave, 'w', encoding='utf-8') as f:
        for filename in filenames:
            filepath = os.path.join(Upload_Folder, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                data = file.read()
                f.write(data)
        
    return filepathtosave  

def detect_platform(lines):
    # 맥용: 첫 번째 줄이 'Date,User,Message' 형식인지 확인
    if len(lines[0].split(',')) == 3 and 'Date' in lines[0] and 'User' in lines[0] and 'Message' in lines[0]:
        return 'mac'
    
    # 윈도우용: 첫 번째 줄에 '님과 카카오톡 대화'가 있고, 이후 줄에 '---------------' 구분선이 있으면 윈도우로 인식
    if '님과 카카오톡 대화' in lines[0] and '저장한 날짜' in lines[1]:
        for line in lines[2:]:
            if '---------------' in line:
                return 'windows'
    
    # 갤럭시용: 첫 번째 줄에 '님과 카카오톡 대화'가 있고, 이후에 날짜 및 시간 패턴이 있는지 확인
    if '님과 카카오톡 대화' in lines[0]:
        for line in lines[2:]:
            if re.match(r'\d{4}년 \d{1,2}월 \d{1,2}일 \s*[오전|오후|AM|PM]{1,2} \d{1,2}:\d{2},', line):
                return 'galaxy'

    # 알 수 없는 형식
    return 'unknown'

# 채팅 필터링 함수
def filter_chat(filepathtosave, name):
    if not os.path.exists(filepathtosave):
        print(f"파일 존재 안 함: {filepathtosave}")
        return
    
    try:
        with open(filepathtosave, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"파일 문장 수: {len(lines)}")
    except Exception as e:
        print(f"파일 읽기 실패: {e}")
        return

    platform = detect_platform(lines)
    print(f"감지된 플랫폼: {platform}")

    filtered_chat = []

    if platform == 'mac':
        for line in lines[1:]:  # 첫 번째 줄은 헤더이므로 제외
            parts = line.strip().split(',', 2)  
            if len(parts) == 3:
                _, user, message = parts
                user = user.strip('"')
                message = message.strip('"')
                if message:
                    filtered_chat.append(f"{user}: {message}")

    elif platform == 'windows':
        time_pattern = re.compile(r'\[오[전후] \d{1,2}:\d{2}\]')
        date_pattern = re.compile(r'--------------- \d{4}년 \d{1,2}월 \d{1,2}일 [가-힣]+요일 ---------------')
        lines = lines[3:]
        for line in lines:
            new_line = time_pattern.sub('', line)
            new_line = date_pattern.sub('', new_line)
            filtered_chat.append(new_line.strip())

    elif platform == 'galaxy':
        date_time_pattern = re.compile(r'\d{4}년 \s*\d{1,2}월 \s*\d{1,2}일 \s*[오전|오후|AM|PM]{1,2} \s*\d{1,2}:\d{2},?')
        for line in lines:
            cleaned_line = date_time_pattern.sub('', line).strip()
            if cleaned_line:
                filtered_chat.append(cleaned_line)

    else:
        print("알 수 없는 형식입니다.")
        return

    if not filtered_chat:
        print("채팅 내용을 찾을 수 없습니다.")
        return
    
    filterfile = os.path.join(os.path.dirname(filepathtosave), 'filtered_chat.txt')
    try:
        with open(filterfile, 'w', encoding='utf-8') as file:
            file.write("\n".join(filtered_chat))
        print(f"필터링 채팅 저장: {filterfile}")
        limit_tokens_from_recent(filterfile)

    except Exception as e:
        print(f"필터링 채팅 저장 에러 발생: {e}")
        return
    
    return filterfile

# gpt 응답
def gpt_response(filterfile, name, user_message=None):
    chat_history = load_chat_history(name)
    myname = session.get('myname')
    print(f"내 이름: {myname}") 

    if not chat_history:
        try:
            with open(filterfile, 'r', encoding='utf-8') as f:
                filtered_data = f.read()
            print("필터링 파일 읽기 성공")
        except Exception as e:
            print(f"필터링 파일 읽기 실패: {e}")
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
        print(f"Error during GPT request: {e}")
        return None

def create_app():
    app = Flask(__name__)
    app.secret_key = 'aa8pepole'
    
    if not os.path.exists(Upload_Folder):
        os.makedirs(Upload_Folder)

    bp = Blueprint('fileupload', __name__, url_prefix='/fileupload')

    @bp.route('/', methods=['GET', 'POST'])
    def upload_file():
        name = session.get('name')
        print("upload_file 실행 성공")
        
        if os.path.exists(Upload_Folder):
            for file in os.scandir(Upload_Folder):
                os.remove(file.path)
            print("Upload folder 내 파일 삭제")
        
        if request.method == 'POST':
            print("POST 받음")
            
            files = request.files.getlist('savefile')
            for file in files:
                filename = file.filename
                filepathtosave = os.path.join(Upload_Folder, filename)
                file.save(filepathtosave)
                print(f"File 저장: {filename}")
            
            merge_file_path = extraction()
            print(f"Merged file 경로: {merge_file_path}")

            filter_chat(merge_file_path, name)
            
            return redirect(url_for('fileupload.result'))

        return render_template('submit.html', name=name)

    @bp.route('/result')
    def result():
        name = session.get('name')
        return render_template('result.html', name=name)

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
        session['myname'] = myname
        return redirect(url_for('yourname'))

    @app.route('/yourname')
    def yourname():
        return render_template('yourname.html')

    @app.route('/yourname/submit')
    def submit():
        global name
        name = request.args.get('name')
        session['name'] = name
        return redirect(url_for('fileupload.upload_file'))

    @app.route('/send_message', methods=['POST'])
    def send_message():
        global name
        data = request.get_json()
        user_message = data['message']

        merge_file_path = os.path.join(Upload_Folder, 'merge.txt')
        filter_file = filter_chat(merge_file_path, name)

        if filter_file:
            reply = gpt_response(filter_file, name, user_message)
            if reply:
                return {'reply': reply}
            else:
                return {'error': 'GPT 응답 생성 중 오류가 발생했습니다.'}
        else:
            return {'error': '필터링 파일 생성 중 오류가 발생했습니다.'}

    return app

if __name__ == '__main__':
    app = create_app()
    app.run('0.0.0.0', port=9005, debug=True)
