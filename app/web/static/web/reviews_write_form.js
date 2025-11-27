let selectedRating = 0;
let selectedImages = [];

document.addEventListener('DOMContentLoaded', function() {
    initRatingStars();
    initImageUpload();
    initForm();
});

function initRatingStars() {
    const stars = document.querySelectorAll('.rating_star');
    const ratingText = document.getElementById('ratingText');

    stars.forEach((star, index) => {
        star.addEventListener('click', function() {
            selectedRating = index + 1;
            updateStarDisplay();
            ratingText.textContent = `${selectedRating}점`;
        });

        star.addEventListener('mouseenter', function() {
            highlightStars(index + 1);
        });
    });

    document.querySelector('.rating_input').addEventListener('mouseleave', function() {
        updateStarDisplay();
    });
}

function highlightStars(rating) {
    const stars = document.querySelectorAll('.rating_star');
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('hover');
        } else {
            star.classList.remove('hover');
        }
    });
}

function updateStarDisplay() {
    const stars = document.querySelectorAll('.rating_star');
    stars.forEach((star, index) => {
        star.classList.remove('hover');
        if (index < selectedRating) {
            star.classList.add('selected');
        } else {
            star.classList.remove('selected');
        }
    });
}

function initImageUpload() {
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');

    imageInput.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);
        selectedImages = files;
        displayImagePreview(files);
    });
}

function displayImagePreview(files) {
    const imagePreview = document.getElementById('imagePreview');
    imagePreview.innerHTML = '';

    files.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const previewItem = document.createElement('div');
            previewItem.className = 'preview_item';
            previewItem.innerHTML = `
                <img src="${e.target.result}" alt="미리보기" class="preview_image">
                <button type="button" class="remove_image" onclick="removeImage(${index})">×</button>
            `;
            imagePreview.appendChild(previewItem);
        };
        reader.readAsDataURL(file);
    });
}

function removeImage(index) {
    selectedImages.splice(index, 1);
    displayImagePreview(selectedImages);
}

function initForm() {
    const form = document.getElementById('reviewForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        submitReview();
    });
}

function submitReview() {
    const title = document.getElementById('reviewTitle').value;
    const content = document.getElementById('reviewContent').value;

    if (!title.trim()) {
        alert('제목을 입력하세요.');
        return;
    }

    if (!content.trim()) {
        alert('후기 내용을 입력하세요.');
        return;
    }

    if (selectedRating === 0) {
        alert('별점을 선택하세요.');
        return;
    }

    // 후기 등록 로직
    console.log('후기 등록:', {
        title,
        content,
        rating: selectedRating,
        images: selectedImages
    });

    showSuccessPage();
}

function showSuccessPage() {
    document.querySelector('.panel_case').innerHTML = `
        <div class="upload_success_container">
            <div class="success_content">
                <div class="success_icon">✓</div>
                <h1 class="success_title">후기 등록 완료</h1>
                <p class="success_message">후기가 성공적으로 등록되었습니다.<br>다른 사람들에게 도움이 되는 후기를 작성해 주셔서 감사합니다!</p>
            </div>
            <div class="success_buttons">
                <button class="btn_primary single_button" onclick="goBack()">후기 목록으로</button>
            </div>
        </div>
    `;
}