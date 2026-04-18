let prevImg;

if ('scrollRestoration' in history) {
    history.scrollRestoration = 'manual';
}

const PENDING_SCROLL_KEY = 'pendingScrollRestore';

document.addEventListener('DOMContentLoaded', () => {
    setupNotifications();
    setupLogout();
    setupStarRatings();
    renderDisplayStars();
    setupScrollPreservingForms();
    setupScrollPreservingLinks();
    restorePendingScroll();

    const picPreview = document.getElementById('picPreview');
    if(picPreview) prevImg = picPreview.src;

    const fileInput = document.querySelector('input[type="file"]')
    if(fileInput) fileInput.onchange = handleFile;
});

function setupScrollPreservingForms() {
    document.querySelectorAll('form[data-preserve-scroll]').forEach(form => {
        form.addEventListener('submit', savePendingScroll);
    });
}

function setupScrollPreservingLinks() {
    document.querySelectorAll('a[data-preserve-scroll]').forEach(link => {
        link.addEventListener('click', event => {
            // Ignore modifier-key clicks and non-primary buttons so new-tab behavior still works
            if (event.defaultPrevented) return;
            if (event.button !== 0) return;
            if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
            savePendingScroll();
        });
    });
}

function savePendingScroll() {
    try {
        sessionStorage.setItem(PENDING_SCROLL_KEY, String(window.scrollY));
    } catch (e) {
        // sessionStorage unavailable (e.g. private mode); silently no-op
    }
}

function restorePendingScroll() {
    let saved;
    try {
        saved = sessionStorage.getItem(PENDING_SCROLL_KEY);
    } catch (e) {
        return;
    }
    if (saved === null) return;
    sessionStorage.removeItem(PENDING_SCROLL_KEY);
    const y = parseInt(saved, 10);
    if (!Number.isNaN(y)) {
        window.scrollTo(0, y);
    }
}

function preserveScrollSubmit(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    savePendingScroll();
    form.submit();
}


function setupNotifications() {
    const notification = document.querySelectorAll('.messages .alert');
    notification.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = "opacity 1.0s";
            alert.style.opacity = 0;
            setTimeout(() =>
            {
                alert.remove();
                // check if ANY alerts remain
                if (document.querySelectorAll('.messages .alert').length === 0) {
                    const container = document.querySelector('.messages');
                    if (container) container.remove();
                }
            }, 1000);
        }, 2500);
    });
}


function setupLogout() {
    const logoutLink = document.getElementById("logout-link");
    const logoutForm = document.getElementById("logout-form");

    if (!logoutLink || !logoutForm) return;

    logoutLink.addEventListener("click", function (e) {
        e.preventDefault();
        logoutForm.submit();
    });
}

function openFileExplorer(){
    document.querySelector('input[type="file"]').click();
}
/*AI citation
//Generated with ChatGPT free version on 04/06/2026
Prompt summary: Requested assistance in how  the edit button to  open the file explorer and display the action buttons
//Purpose: to handle profile upload based on which button is clicked
*/
function handleFile (){
    const newImage = this.files[0];
    let preview = document.getElementById('picPreview');
    if(newImage){
        const reader = new FileReader();
        reader.onload = function(e)
        {
            preview.src = e.target.result;

            document.getElementById('editBtn').style.display='none';
            document.getElementById('actionBtns').style.display='block';
        };
        reader.readAsDataURL(newImage);
    }
}


function cancelUploadOperation(){
    document.querySelector('input[type="file"]').value="";
    document.getElementById('picPreview').src = prevImg;
    document.getElementById('editBtn').style.display='block';
    document.getElementById('actionBtns').style.display='none';

}

function setupStarRatings() {
    document.querySelectorAll('.star-rating').forEach(group => {
        const fieldName = group.dataset.field;
        const hiddenInput = group.parentElement.querySelector('input[name="' + fieldName + '"]');
        const stars = group.querySelectorAll('.star');

        stars.forEach(star => {
            star.addEventListener('mouseenter', () => {
                const val = parseInt(star.dataset.value);
                stars.forEach(s => {
                    s.classList.toggle('hovered', parseInt(s.dataset.value) <= val);
                });
            });

            star.addEventListener('mouseleave', () => {
                stars.forEach(s => s.classList.remove('hovered'));
            });

            star.addEventListener('click', () => {
                const val = parseInt(star.dataset.value);
                const currentVal = parseInt(hiddenInput.value);
                if (currentVal === val) {
                    hiddenInput.value = '';
                    stars.forEach(s => s.classList.remove('selected'));
                } else {
                    hiddenInput.value = val;
                    stars.forEach(s => {
                        s.classList.toggle('selected', parseInt(s.dataset.value) <= val);
                    });
                }
            });
        });
    });
}

function renderDisplayStars() {
    document.querySelectorAll('.stars-display').forEach(container => {
        const raw = container.dataset.rating;
        if (!raw) {
            container.innerHTML = '<span class="no-rating">No rating</span>';
            return;
        }
        const val = parseFloat(raw);
        let html = '';
        for (let i = 1; i <= 5; i++) {
            if (i <= Math.floor(val)) {
                html += '<span class="star-filled">&#9733;</span>';
            } else if (i === Math.ceil(val) && val % 1 >= 0.25) {
                html += '<span class="star-half">&#9733;</span>';
            } else {
                html += '<span class="star-empty">&#9733;</span>';
            }
        }
        container.innerHTML = html;
    });
}