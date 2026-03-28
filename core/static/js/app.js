document.addEventListener('DOMContentLoaded', () => {
    setupNotifications();
    setupLogout();
});


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