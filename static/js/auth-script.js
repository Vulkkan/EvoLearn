var buttons = document.getElementsByTagName("button");

for (var i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener("click", async function (event) {

        // Animate header
        document.getElementById('heading').classList.remove("h1Change");
        document.getElementById('under-line').classList.remove("h1Change");
        void document.getElementById('heading').offsetWidth;
        void document.getElementById('under-line').offsetWidth;
        document.getElementById('heading').classList.add("h1Change");
        document.getElementById('under-line').classList.add("h1Change");

        // Enables selected button, disabled the rest
        // Attach an event listener to each button except the "go" button
        if (this.id === "go") return;

        // Enable the clicked button, disable the rest
        for (var j = 0; j < buttons.length; j++) {
            if (buttons[j].id !== "go") {
                buttons[j].classList.add("disabled"); // Disable all except "go"
            }
        }

        // Enable the clicked button
        this.classList.remove("disabled");

        // Check which button was clicked
        if (this.textContent.trim() === "Sign Up") {
            // Animate header, unhide 'Name' field
            document.getElementById('heading').innerText = "Sign Up";
            document.getElementById('name').classList.remove('hidden');

            // Animate para form
            document.getElementById('para').innerHTML = "Password Suggestions? <br><span>Click Here!</span>";
            document.getElementById('para').style.transform = 'translateX(-30px)';
            document.getElementById('para').style.color = 'black';


        } else if (this.textContent.trim() === "Sign In") {
            // Animate header, hide 'Name' field
            document.getElementById('heading').innerText = "Sign In";
            document.getElementById('name').classList.add('hidden');

            // Animate para form
            document.getElementById('para').innerHTML = "Forgot Password? <br><span>Click Here</span>";
            document.getElementById('para').style.transform = 'translateX(-50px)';
            document.getElementById('para').style.color = 'black';
        } 
    });
}

document.addEventListener("DOMContentLoaded", function () {
    var go = document.querySelector("#go");

    go.addEventListener("click", function () {
        var email = document.querySelector("#email input").value.trim();
        var password = document.querySelector("#password input").value.trim();

        // Navigate to screen if email & password
        // if (email && password) {
        //     window.location.href = "chat";
        // } else {
        //     // Return error
        //     document.getElementById('para').innerHTML = "*Enter a random <br> email and password";
        //     document.getElementById('para').style.transform = 'translateX(-50px)';
        //     document.getElementById('para').style.color = 'red';
        // }
        window.location.href = "select_profile";
    });
});