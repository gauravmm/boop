"use strict";

// This is based loosely on the tutorial at:
// https://developers.google.com/web/fundamentals/getting-started/codelabs/push-notifications/

function $(id) {
    return document.getElementById(id);
}

function handleSetupError(error){
    console.error('Service Worker Error', error);
    $("notif-enable").className = "button";
    $("notif-enable-err").className = "error";
    $("notif-enable-err-msg").innerHTML = error;
}

var swRegistration = null;
$("notif-enable").onclick = function() {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
        console.log('Service Worker and Push is supported');

        navigator.serviceWorker.register('sw.js')
        .then(function(swReg) {
            console.log('Service Worker is registered', swReg);
            swRegistration = swReg;
        })
        .catch(handleSetupError);
    } else {
        handleSetupError("Push messaging is not supported by your device.")
    }
}
