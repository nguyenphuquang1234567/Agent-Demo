const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const imageUpload = document.getElementById('image-upload');
const imagePreviewContainer = document.getElementById('image-preview-container');
const imagePreview = document.getElementById('image-preview');
const removeImageBtn = document.getElementById('remove-image');
const themeToggle = document.getElementById('theme-toggle');
const loadingIndicator = document.getElementById('loading-indicator');

let sessionId = null;
let currentFile = null;

// Khởi tạo phiên làm việc
async function initSession() {
    try {
        const response = await fetch('/api/chat/start', { method: 'POST' });
        const data = await response.json();
        sessionId = data.session_id;
        appendMessage(data.message, 'ai-message');
    } catch (error) {
        console.error('Error starting session:', error);
        appendMessage('Xin lỗi, không thể kết nối đến máy chủ lúc này. Đảm bảo Backend FastAPI đang chạy.', 'ai-message');
    }
}

// Hàm thêm tin nhắn vào giao diện
function appendMessage(content, className, imageUrl = null) {
    const div = document.createElement('div');
    div.className = `message ${className}`;
    
    let innerHTML = '';
    if (imageUrl) {
        innerHTML += `<img src="${imageUrl}" class="message-image" alt="Uploaded image">`;
    }
    
    if (className === 'ai-message') {
        innerHTML += marked.parse(content);
    } else {
        innerHTML += `<p>${content}</p>`;
    }
    
    div.innerHTML = innerHTML;
    
    // Chèn vào trước loading indicator
    chatBox.insertBefore(div, loadingIndicator);
    scrollToBottom();
}

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Xử lý textarea tự động tăng chiều cao
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// Gửi tin nhắn bằng phím Enter (không có shift)
messageInput.addEventListener('keydown', function(e) {
    // Bỏ qua phím Enter nếu đang gõ dấu tiếng Việt (IME composing)
    if (e.isComposing || e.keyCode === 229) {
        return;
    }
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.requestSubmit();
    }
});

// Upload và preview ảnh
imageUpload.addEventListener('change', function(e) {
    if (this.files && this.files[0]) {
        currentFile = this.files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            imagePreviewContainer.style.display = 'inline-block';
        }
        reader.readAsDataURL(currentFile);
    }
});

removeImageBtn.addEventListener('click', function() {
    currentFile = null;
    imageUpload.value = '';
    imagePreviewContainer.style.display = 'none';
});

let isSubmitting = false;

// Xử lý form submit
chatForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (isSubmitting) return;
    
    const messageText = messageInput.value.trim();
    if (!messageText && !currentFile) return;
    if (!sessionId) {
        alert("Hệ thống chưa kết nối xong, vui lòng chờ...");
        return;
    }
    
    isSubmitting = true;
    
    // Lưu lại thông tin trước khi reset UI
    const fileToSend = currentFile;
    const imageUrl = currentFile ? imagePreview.src : null;
    
    // Hiển thị tin nhắn người dùng
    appendMessage(messageText, 'user-message', imageUrl);
    
    // Reset inputs
    messageInput.blur(); // Ép hệ điều hành kết thúc việc gõ dấu (IME)
    messageInput.value = '';
    messageInput.style.height = 'auto';
    messageInput.focus(); // Đưa con trỏ chuột quay lại để chat tiếp
    
    currentFile = null;
    imageUpload.value = '';
    imagePreviewContainer.style.display = 'none';
    
    // Hiện loading
    loadingIndicator.style.display = 'block';
    scrollToBottom();
    
    // Gọi API
    try {
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('message', messageText || "Tôi gửi một hình ảnh cần tư vấn."); 
        
        if (fileToSend) {
            formData.append('file', fileToSend);
        }
        
        const response = await fetch('/api/chat/message', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            appendMessage(data.response, 'ai-message');
        } else {
            appendMessage(`Lỗi: ${data.detail || 'Có lỗi xảy ra'}`, 'ai-message');
        }
    } catch (error) {
        console.error('API Error:', error);
        appendMessage('Không thể kết nối đến AI. Vui lòng thử lại!', 'ai-message');
    } finally {
        loadingIndicator.style.display = 'none';
        isSubmitting = false;
    }
});

// Theme Toggle
themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-theme');
    const icon = themeToggle.querySelector('i');
    if (document.body.classList.contains('dark-theme')) {
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
    }
});

// Bắt đầu ngay khi load web
window.addEventListener('DOMContentLoaded', initSession);
