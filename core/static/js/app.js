let prevImg;
document.addEventListener('DOMContentLoaded', () => {
    setupNotifications();
    setupLogout();

    const picPreview = document.getElementById('picPreview');
    if(picPreview) prevImg = picPreview.src;

    const fileInput = document.querySelector('input[type="file"]')
    if(fileInput) fileInput.onchange = handleFile;
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

function search(){
    var input = document.getElementById("mySearch").value.toLowerCase();
    let reviews = document.getElementsByClassName('review-item');

    for(let i=0;i<reviews.length;i++){
        let cioName = reviews[i].getElementsByClassName("cio.name")[0];
        let inputValue = cioName.textContent || cioName.innerText;

        if(inputValue.toLowerCase().indexOf(input)>-1){
            reviews[i].style.display = "";
        }
        else
        {
            reviews[i].style.display = "none";
        }
    }
}

    function searchCios()
    {
        var input = document.getElementById("mySearch").value.toLowerCase();
        let cios = document.getElementsByClassName('cio-item');

        for(let i=0;i<cios.length;i++)
        {
            let cioName = cios[i].getElementsByClassName("cio-name")[0];
            let inputValue = cioName.textContent || cioName.innerText;

            if(inputValue.toLowerCase().startsWith(input))
            {
                cios[i].style.display = "";
            }
            else
            {
                cios[i].style.display = "none";
            }
        }
}