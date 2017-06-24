"use strict";

// This is based loosely on the tutorial at:
// https://developers.google.com/web/fundamentals/getting-started/codelabs/push-notifications/

var PUBLIC_KEY="BKgErtbhIt2ODORN94yWQsX-etN4RwaJc3Z7NTD_litd4Zmu3oIN39tjXHd8bEMt5Fl94r9I6YakfEHtWijS96Y";

function $(id) {
    return document.getElementById(id);
}

function handleSetupError(error){
    console.error('Service Worker Error', error);
    $("notif-enable").className = "button";
    $("notif-enable").disabled = true;
    $("notif-enable-err").className = "error";
    $("notif-enable-err-msg").innerHTML = error;
}

var swRegistration = null;
if ('serviceWorker' in navigator && 'PushManager' in window) {
    console.log('Service Worker and Push is supported');
    navigator.serviceWorker.register('boopservice.js')
    .then(function(swReg) {
        console.log('Service Worker is registered', swReg);
        swRegistration = swReg;
        initializeUI()
    }).catch(handleSetupError);
} else {
    handleSetupError("Push messaging is not supported by your device.")
    $("notif-enable").onclick = null;
}

var isSubscribed = false;
function initializeUI() {
    swRegistration.pushManager.getSubscription()
    .then(function(subscription) {
        isSubscribed = !(subscription === null);
        if (isSubscribed) {
            console.log('User IS subscribed.');
            $("notif-enable").className="button button-selected";
        } else {
            console.log('User is NOT subscribed.');
            $("notif-enable").className="button button-active";
        }


        $("notif-enable").onclick = function() {
            $("notif-enable").disabled = true;
            $("notif-enable").className = "button button-processing";
            if (isSubscribed) {
                // TODO: Unsubscribe user
            } else {
                // subscribeUser();
            }
        }
        $("notif-enable").disabled = false;
    }).catch(handleSetupError);
}

