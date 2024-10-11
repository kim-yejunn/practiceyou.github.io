const form = document.getElementById('chat-form');
const chatBox = document.getElementById('chat-box');
const userMessage = document.getElementById('user-message');

userMessage.addEventListener('focus', () => {
    adjustChatBoxHeight();
});

userMessage.addEventListener('blur', () => {
    resetChatBoxHeight();
});

function setViewportHeight() {
    // 뷰포트 높이를 계산하여 CSS 변수로 설정
    document.documentElement.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);
}
setViewportHeight();

// 이벤트 리스너 추가
window.addEventListener('resize', setViewportHeight);
window.addEventListener('orientationchange', setViewportHeight);

function adjustChatBoxHeight() {
    const viewportHeight = window.visualViewport ? window.visualViewport.height : window.innerHeight;
    const profileHeight = document.querySelector('.gpt-profile').offsetHeight;
    const inputBoxHeight = document.querySelector('.chat-input-box').offsetHeight;

    chatBox.style.height = `${viewportHeight - profileHeight - inputBoxHeight}px`;
}

function resetChatBoxHeight() {
    const profileHeight = document.querySelector('.gpt-profile').offsetHeight;
    const inputBoxHeight = document.querySelector('.chat-input-box').offsetHeight;

    chatBox.style.height = `calc(100vh - ${profileHeight + inputBoxHeight}px)`;
}

// 초기 높이 설정
resetChatBoxHeight();






// form.addEventListener('submit', function (e) {
//     e.preventDefault();
    
//     const message = userMessage.value.trim();
//     if (message) {
//         // 사용자 메시지 표시 (오른쪽)
//         const userDiv = document.createElement('div');
//         userDiv.className = 'user-message';
//         userDiv.innerText = message;
//         chatBox.appendChild(userDiv);

//         // 서버에 메시지 전송
//         fetch('/send_message', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({ message: message })
//         })
//         .then(response => response.json())
//         .then(data => {
//             // GPT 응답을 한 문장씩 나누어 출력
//             const sentences = data.reply.split(/(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s/g); // 문장 단위로 분리
//             sentences.forEach((sentence, index) => {
//                 setTimeout(() => {
//                     const gptDiv = document.createElement('div');
//                     gptDiv.className = 'gpt-message';
//                     gptDiv.innerText = sentence.trim();
//                     chatBox.appendChild(gptDiv);
                    
//                     // 자동 스크롤
//                     chatBox.scrollTop = chatBox.scrollHeight;
//                 }, index * 1000); // 1초 간격으로 문장 출력
//             });
//         });

//         userMessage.value = '';
//     }
// });



form.addEventListener('submit', function (e) {
    e.preventDefault();
    
    const message = userMessage.value.trim();
    if (message) {
        // 사용자 메시지 표시 (오른쪽)
        const userDiv = document.createElement('div');
        userDiv.className = 'user-message';
        userDiv.innerText = message;
        chatBox.appendChild(userDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

        // 서버에 메시지 전송
        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            // GPT 응답을 한 문장씩 나누어 출력
            const sentences = data.reply.split(/(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s/g); // 문장 단위로 분리
            sentences.forEach((sentence, index) => {
                setTimeout(() => {
                    // "입력 중..." 말풍선 표시
                    const typingIndicator = document.createElement('div');
                    typingIndicator.className = 'gpt-message typing-indicator';
                    typingIndicator.innerText = '입력 중...';
                    chatBox.appendChild(typingIndicator);
                    chatBox.scrollTop = chatBox.scrollHeight;

                    setTimeout(() => {
                        // "입력 중..." 말풍선 제거
                        chatBox.removeChild(typingIndicator);

                        // GPT 메시지와 프로필을 포함하는 div.gpt-msg 생성
                        const gptMsgDiv = document.createElement('div');
                        gptMsgDiv.className = 'gpt-msg';

                        // // GPT 프로필 추가
                        // const gptProfileDiv = document.createElement('div');
                        // gptProfileDiv.className = 'gpt-name';
                        // gptProfileDiv.innerText = yourName; // Flask 변수 사용
                        // gptMsgDiv.appendChil d(gptProfileDiv);

                        // GPT 메시지 추가
                        const gptDiv = document.createElement('div');
                        gptDiv.className = 'gpt-message';
                        gptDiv.innerText = sentence.trim();
                        gptMsgDiv.appendChild(gptDiv);

                        // gpt-msg를 chatBox에 추가
                        chatBox.appendChild(gptMsgDiv);
                        
                        // 자동 스크롤
                        chatBox.scrollTop = chatBox.scrollHeight;
                    }, 1000); // 1초 후에 메시지 추가
                }, index * 2000); // 2초 간격으로 "입력 중..."과 메시지 출력
            });
        });

        userMessage.value = '';
    }
});

