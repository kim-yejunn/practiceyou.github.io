const form = document.getElementById('chat-form');
const chatBox = document.getElementById('chat-box');
const userMessage = document.getElementById('user-message');

form.addEventListener('submit', function (e) {
    e.preventDefault();
    
    const message = userMessage.value.trim();
    if (message) {
        // 사용자 메시지 표시 (오른쪽)
        const userDiv = document.createElement('div');
        userDiv.className = 'user-message';
        userDiv.innerText = message;
        chatBox.appendChild(userDiv);

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
                    const gptDiv = document.createElement('div');
                    gptDiv.className = 'gpt-message';
                    gptDiv.innerText = sentence.trim();
                    chatBox.appendChild(gptDiv);
                    
                    // 자동 스크롤
                    chatBox.scrollTop = chatBox.scrollHeight;
                }, index * 1000); // 1초 간격으로 문장 출력
            });
        });

        userMessage.value = '';
    }
});
