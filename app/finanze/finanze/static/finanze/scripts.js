// This values need to be global
// as input are dublicated for responsiveness reasons
var newPassword1, newPassword2;
var updateNewPassword1 = function (index) {
    newPassword1 = document.getElementsByName('new_password1')[index].value;
}
var updateNewPassword2 = function(index) {
    newPassword2 = document.getElementsByName('new_password2')[index].value;
}
var xhrparamsFactory = function() {
    csrf = document.getElementsByName('csrfmiddlewaretoken')[0];
    params = {
        csrfmiddlewaretoken: csrf.value,
    };
    return params;
}
var userPasswordChange = function (index) {
    old_password = document.getElementsByName('old_password')[0];
    new_password1 = document.getElementsByName('new_password1')[index];
    new_password2 = document.getElementsByName('new_password2')[index];
    old_password.classList.remove('is-valid', 'is-invalid');
    new_password1.classList.remove('is-valid', 'is-invalid');
    new_password2.classList.remove('is-valid', 'is-invalid');
    params = xhrparamsFactory();
    params["old_password"] = old_password.value;
    params["new_password1"] = newPassword1;
    params["new_password2"] = newPassword2;
    
    var XHR = new XMLHttpRequest();
    XHR.addEventListener('load', function () {
        responseData = JSON.parse(XHR.responseText);
        if (responseData.error == undefined) {
            new_password2.classList.add('is-valid');
            setTimeout(() => {
                window.location.assign("/login");
            }, 1000);
        } else {
            responseData.error.forEach(name => {
                if (name == "old_password"){
                    document.getElementsByName(name)[0].classList.add('is-invalid');
                }else{ // new_passwordX
                    document.getElementsByName(name)[index].classList.add('is-invalid');
                }
            });
        }
    });
    XHR.addEventListener('error', function () {
        console.log(XHR.statusText);
    });
    var search = new URLSearchParams(params);
    XHR.open("POST", "/profile/password-change");
    XHR.send(search);
};
var userParamChange = function(inputName) {
    var inputEl = document.getElementsByName(inputName)[0];
    inputEl.classList.remove('is-valid');
    params = xhrparamsFactory();
    params[inputName] = inputEl.value
    var XHR = new XMLHttpRequest();
    XHR.addEventListener('load', function () {
        responseData = JSON.parse(XHR.responseText);
        if(responseData.error == undefined){
            inputEl.classList.add('is-valid');
        }else{

        }
    });
    XHR.addEventListener('error', function () {
        console.log(XHR.statusText);
    });
    var search = new URLSearchParams(params);
    
    XHR.open("POST", "/profile/");
    XHR.send(search);
}
window.addEventListener("load", function(event) {
    usernameInput = document.getElementById('username');
    usernameInput.addEventListener("change", function(event) {
        userParamChange(this.getAttribute('name'));
    });
    emailInput = document.getElementById('email');
    emailInput.addEventListener("change", function(event) {
        userParamChange(this.getAttribute('name'));
    });

});