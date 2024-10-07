document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const fileInput = form.querySelector('input[type="file"]');
        
        if (fileInput.files.length === 0) {
            alert('파일을 선택해주세요.');
            return;
        }
        
        fetch('/fileupload/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            if (data.success) {
                window.location.href = '/fileupload/result';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('오류가 발생했습니다.');
        });
    });
});