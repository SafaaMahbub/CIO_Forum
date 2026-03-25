document.addEventListener('DOMContentLoaded', () => {
    const notification = document.querySelectorAll('.messages .alert');
    notification.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = "opacity 1.0s";
            alert.style.opacity = 0;
            setTimeout(() =>
            {
                alert.remove();
                const container = document.querySelector('.messages');
                if (container && container.children.length === 0) {
                    container.remove();
                    container.visible = False;
                }
            }, 1000);
        }, 2500);
    });
});