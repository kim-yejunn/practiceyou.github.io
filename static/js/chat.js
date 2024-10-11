const form = document.getElementById('chat-form');
const chatBox = document.getElementById('chat-box');
const userMessage = document.getElementById('user-message');


//화면 비율 관련
const windowInnerHeight = window.innerHeight;
const viewportHeight = parseInt(visualViewport.height);
let isKeyboard = false;

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
                        // gptMsgDiv.appendChild(gptProfileDiv);

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



// EX) 키보드 ON - scroll 이벤트 
if(windowInnerHeight > viewportHeight){ // 키보드 ON
    isKeyboard = true;
    viewportwrap.style.height = `${viewportHeight}px`;
    window.addEventListener('scroll',handleWindowScroll);
    visualViewport.addEventListener("scroll", handleViewportScroll);
  }else{  // 키보드 OFF - scroll 이벤트 해제
    isKeyboard = false;
    viewportwrap.style.height = "100%";
    window.removeEventListener('scroll',handleWindowScroll);
    visualViewport.removeEventListener("scroll", handleViewportScroll);
  }
  
  // scroll event
  function handleWindowScroll(){
    let viewportTopGap = parseInt(visualViewport.pageTop - visualViewport.offsetTop);
    let translateY = parseInt(window.scrollY - viewportTopGap);
    // 👇 scroll 변화에 따라 viewport div 이동
    viewportwrap.style.transform = `translateY(${translateY}px)`;
  }
  // viewport scroll 
  function handleViewportScroll (e){ 
    // viewport scroll
    const viewportScrollY = parseInt(e.target.offsetTop);
    // IOS에서는 사용하지 않고 확인용으로만 👀
    // viewport scroll 값을 계산한다면 사용할 수 있습니다.
  }
// 가상 영역까지 스크롤 내려가는 것을 방지
if(window.scrollY + visualViewport.height > document.body.offsetHeight - 2){ 
    window.scrollTo(0, document.body.offsetHeight - visualViewport.height-1);
}