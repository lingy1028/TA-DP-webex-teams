document.addEventListener("DOMNodeInserted", function (event) {

    if (event.target.className && event.target.className.startsWith("form-")) {
        h = event.target.querySelector('.help-block')
        if (h) {
            replace_text = "by clicking the below button";
            h.innerHTML = h.innerHTML.replace(replace_text, "<div><a href='#' class='btn btn-primary' onclick=clickEvent()>Generate Tokens</a>");
        }
    }
}, false);

function clickEvent() {
    let client_id = getInputValue('additional_parameters-client_id')
    let client_secret = getInputValue('additional_parameters-client_secret')
    let redirect_uri = getInputValue('additional_parameters-redirect_uri')
    let encode_redirect_uri = encodeURIComponent(redirect_uri)

    var settings = {
        "url": "/en-US/splunkd/__raw/services/webex-teams-oauth",
        "method": "POST",
        "timeout": 0,
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"

        },
        "data": $.param({ "redirect_uri": redirect_uri, "client_id": client_id, "client_secret": client_secret}),
    };
    $.ajax(settings).done(function (response) {
        console.log("response", response["method"]);
    });
    console.log("redirect_uri", redirect_uri)
    console.log("encode_redirect_uri", encode_redirect_uri)
    console.log("client_id", client_id)
    console.log("client_secret", client_secret)
    url = `https://webexapis.com/v1/authorize?client_id=${client_id}&response_type=code&redirect_uri=${encode_redirect_uri}&scope=spark%3Akms%20audit%3Aevents_read%20spark-compliance%3Aevents_read&state=set_state_here`
    console.log("Clicked URL : " + url);
    window.open(url, 'popup', 'width=700,height=700');
    return false;
}

function getInputValue(inputId) {
    let inputBox = document.getElementById(inputId);
    inputBox.onkeyup = function () {
        let inputValue = this.value;
        return inputValue
    }
    let inputValue = inputBox.onkeyup()
    return inputValue
}



function setRESTHandler(){
    let full_url_arr = window.location.href.split("/");
    $("#additional_parameters-redirect_uri").val(full_url_arr[0] + "/" + full_url_arr[1] + "/" + full_url_arr[2]  + "/" + full_url_arr[3]  + "/" + "splunkd/__raw/services/webex-teams-oauth");
}

document.addEventListener("DOMContentLoaded", function(event) { 
    //do work
    setTimeout(function(){ 
        setRESTHandler();
    }, 5000);    
});