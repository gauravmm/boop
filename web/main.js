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

// Decode JSON if fetch is processed successfully.
function jsonMap(r) {
    if(!r.ok)
        return Promise.reject(r.status + " " + r.statusText);
    return r.json()
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
        $("pusher-new").disabled = false;
        $("pusher-new").className = "button button-active";
        
        if(device_name)
            $("device-name").innerText = device_name;

        $("device-name").onclick = function() {
            alert("Renaming has not been implemented, so if you want to rename this, it might require some manual tweaking.")
            getAndUpdateName(true)
        }

        updateButton();
    }).catch(handleSetupError);
    getDeviceStatus();
}

function deleteDevice(node, url) {
    node.parentNode.removeChild(node);
    fetch(url).then(jsonMap).reject(handleSetupError);
    getDeviceStatus();
}

function durationString(dur) {
    if (dur < 30)	            return "just now";
    if (dur < 60 * 1.5)	        return "a minute ago";
    if (dur < 60 * 2.5)	        return "a few minutes ago";
    if (dur < 60 * 7.5)	        return "five minutes ago";
    if (dur < 60 * 12.5)	    return "ten minutes ago";
    if (dur < 60 * 20)	        return "fifteen minutes ago";
    if (dur < 60 * 45)	        return "half an hour ago";
    if (dur < 3600 * 1.25)	    return "an hour ago";
    if (dur < 3600 * 2.5)	    return "two hours ago";
    if (dur < 3600 * 8)	        return "a few hours ago";
    if (dur < 3600 * 16)	    return "half a day ago";
    if (dur < 3600 * 32)	    return "a day ago";
    if (dur < 3600 * 24 * 2.5)	return "two days ago";
    if (dur < 3600 * 24 * 5)	return "a few days ago";
    if (dur < 3600 * 24 * 10)	return "a few week ago";
    if (dur < 3600 * 24 * 20)	return "two weeks ago";
    if (dur < 3600 * 24 * 40)	return "a few weeks ago";
    if (dur < 3600 * 24 * 60)	return "a few months ago";
    return "a long time ago";
}

function populateList(node, list) {
    // Remove all children: https://stackoverflow.com/a/22966637
    var cNode = node.cloneNode(false);
    node.parentNode.replaceChild(cNode, node);
    node = cNode

    var nowtime = Math.floor(Date.now() / 1000);

    list.forEach(function(e) {
        var root = document.createElement("li");

        var name = document.createElement("span");
        name.innerText = e.name;
        name.className = "d-name " + e.style.class
        root.appendChild(name);

        var icon = document.createElement("img");
        icon.src = e.style.icon;
        root.appendChild(icon);

        var del = document.createElement("span");
        del.innerText = "remove";
        del.className = "d-x"
        del.onclick = ()=>deleteDevice(del, e.name);
        root.appendChild(del);

        var since = document.createElement("span");
        since.innerText = "Last seen " + durationString(nowtime - e.lastseen);
        since.className = "d-since"
        root.appendChild(since);

        node.appendChild(root);
    });
}

function getDeviceStatus() {
    fetch('/getconn/').then(jsonMap).then(function(response) {
        console.log("Conn:", response)
        populateList($("client-list"), response.clients)
        populateList($("pusher-list"), response.pushers)
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
        $("device-name").innerText = device_name;
    }
    return device_name;
}

function updateSubscriptionOnServer(subscription){
    device_name = getAndUpdateName()
    if (device_name == null)
        return;
    subscription = JSON.stringify(subscription).replace(/\//g,"%2F");
    $("content").innerText=subscription;
    fetch('/register/' + encodeURIComponent(name) + "/" + subscription).then(jsonMap).then(function(response) {
        console.log("Response: ", response);
        if(!response.success)
            return Promise.reject(response.message);
    }).catch(handleSetupError);
}

// Add new client
$("pusher-new").onclick = function() {
    $("pusher-new").disabled = true;
    $("pusher-new").className = "button button-processing";
    device_name = getAndUpdateName()
    if (device_name == null) {
        $("pusher-new").disabled = false;
        $("pusher-new").className = "button button-active";
        return;
    }
    fetch('/addpusher/' + encodeURIComponent(device_name) + "/").then(jsonMap).then(function(response) {
        console.log("Pusher-new: ", response);
        if(!response.success)
            return Promise.reject(response.message);
        $("newpusher-auth").innerText=`echo '${response.auth}' > ~/.boop && chmod 0600 ~/.boop;`;
        $("newpusher-bashrc").innerText=`# Add this to your .bashrc or startup script
# Usage: boop &lt;title&gt; &lt;text&gt; [&lt;option-1&gt; [...]]
function boop {
    local pushstr="$(date +%s)/"
    for arg in "$@"; do
        pushstr="$pushstr$(echo -ne $arg | xxd -plain | tr -d '\\n' | sed 's/\\(..\\)/%\\1/g')/"
    done
    local sig=$(echo -ne "$(cat ~/.boop)/$pushstr" | sha224sum | cut -d" " -f1)
    wget -qO - "${CONFIG.url}push/${device_name}/$sig/$pushstr" 1>/dev/null
}`;
        $("newpusher").className=""
    }).catch(handleSetupError);
}
