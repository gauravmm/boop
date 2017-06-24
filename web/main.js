"use strict";

// This is based loosely on the tutorial at:
// https://developers.google.com/web/fundamentals/getting-started/codelabs/push-notifications/

const PUBLIC_KEY="BKgErtbhIt2ODORN94yWQsX-etN4RwaJc3Z7NTD_litd4Zmu3oIN39tjXHd8bEMt5Fl94r9I6YakfEHtWijS96Y";

function $(id) {
    return document.getElementById(id);
}

function urlB64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

function handleSetupError(error){
    console.error('Setup Error', error);
    $("notif-enable").className = "button button-error";
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
function updateButton() {
    if (Notification.permission === 'denied') {
        handleSetupError("You must give permission for notifications to be displayed.")
        return;
    }
    if (isSubscribed) {
        console.log('User IS subscribed.');
        $("notif-enable").className="button button-selected";
    } else {
        console.log('User is NOT subscribed.');
        $("notif-enable").className="button button-active";
    }
    $("notif-enable").disabled = false;
}
function initializeUI() {
    swRegistration.pushManager.getSubscription()
    .then(function(subscription) {
        isSubscribed = !(subscription === null);
        $("notif-enable").onclick = function() {
            $("notif-enable").disabled = true;
            $("notif-enable").className = "button button-processing";
            if (isSubscribed) {
                unsubscribeUser();
            } else {
                subscribeUser();
            }
            updateButton();
        }
        updateButton();
    }).catch(handleSetupError);
}

function subscribeUser() {
    const applicationServerKey = urlB64ToUint8Array(PUBLIC_KEY);
    swRegistration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: applicationServerKey
    }).then(function(subscription) {
        console.log('User is subscribed.');
        console.log(subscription);
        updateSubscriptionOnServer(subscription);
        isSubscribed = true;
        updateButton();
    }).catch(handleSetupError);
}
function unsubscribeUser() {
    swRegistration.pushManager.getSubscription()
    .then(function(subscription) {
        if (subscription) {
          return subscription.unsubscribe();
        }
    }).catch(handleSetupError)
    .then(function() {
        updateSubscriptionOnServer(null);
        console.log('User is unsubscribed.');
        isSubscribed = false;
        updateButton();
    });
}

function updateSubscriptionOnServer(subscription){
    $("content").innerText=JSON.stringify(subscription);
}

