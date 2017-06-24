"use strict";

// This is based loosely on the tutorial at:
// https://developers.google.com/web/fundamentals/getting-started/codelabs/push-notifications/


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

function handleSetupError(error, recoverable=false){
    console.error('Setup Error', error);
    $("notif-enable-err").className = "error";
    $("notif-enable-err-msg").innerHTML = error;
    if(recoverable)
        return
    $("notif-enable").className = "button button-error";
    $("notif-enable").disabled = true;
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
    const applicationServerKey = urlB64ToUint8Array(CONFIG.server_key);
    swRegistration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: applicationServerKey
    }).then(function(subscription) {
        updateSubscriptionOnServer(subscription);
        isSubscribed = true;
        updateButton();
    }).catch(handleSetupError);
}
function unsubscribeUser() {
    swRegistration.pushManager.getSubscription()
    .then(function(subscription) {
        return subscription && subscription.unsubscribe()
    }).then(function() {
        updateSubscriptionOnServer(null);
        isSubscribed = false;
        updateButton();
    }).catch(handleSetupError);
}

var device_name = localStorage.getItem("name");
function getAndUpdateName(force=false){
    if (device_name == null || device_name == "" || force) {
        device_name = window.prompt("Please assign this device a name:", navigator.appName);
        if (device_name == null || device_name == "") {
            handleSetupError("Please specify a name for this device.", True);
            return null;
        }
        localStorage.setItem("name", device_name);
    }
    return device_name;
}

function updateSubscriptionOnServer(subscription){
    device_name = getAndUpdateName()
    if (device_name == null)
        return;
    subscription = JSON.stringify(subscription);
    $("content").innerText=subscription;
    get('/register/' + encodeURIComponent(name) + "/" + subscription).then(function(response) {
        response = JSON.parse(response)
        console.log("Response: ", response);
        if(!response.success)
            handleSetupError(response.message);
    }).catch(handleSetupError);
}

// Promisified-XMLHttpRequest from:
// https://developers.google.com/web/fundamentals/getting-started/primers/promises#promisifying_xmlhttprequest
function get(url) {
    return new Promise(function(resolve, reject) {
        var req = new XMLHttpRequest();
        req.open('GET', url);
        req.onload = function() {
            if (req.status == 200)
                resolve(req.response);
            reject(Error("Cannot register with server: " + req.statusText));
        };
        req.onerror = () => reject(Error("Cannot register with server: Network Error"));
        req.send();
    });
}
