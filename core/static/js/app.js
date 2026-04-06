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

const prevImg = document.getElementById('picPreview').src;
function openFileExplorer(){
    document.querySelector('input[type="file"]').click();
}

//citation edit
document.querySelector('input[type="file"]').onchange = function (){
    const newImage = this.files[0];
    let preview = document.getElementById('picPreview');
    if(newImage){
        const reader = new FileReader();
        reader.onload = function(e)
        {
            preview.src = e.target.result;

            document.querySelector('editButton').style.display='none';
            document.querySelector('actionBtns').style.display='block';
        };
        reader.readAsDataURL(newImage);
    }



}


function cancelUploadOperation(){
    let fileSrc = document.querySelector('input[type="file"]').value="";



    document.getElementById('picPreview').src = prevImg;

    document.querySelector('editButton').style.display='block';
    document.querySelector('actionBtns').style.display='none';

}