document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('savefile');
    const fileNameDisplay = document.getElementById('file-name-display');

    fileInput.addEventListener('change', () => {
        const files = fileInput.files;
        if (files.length > 0) {
            const fileNames = Array.from(files).map(file => file.name).join(', ');
            fileNameDisplay.textContent = `선택된 파일: ${fileNames}`;
        } else {
            fileNameDisplay.textContent = '';
        }
    });
});