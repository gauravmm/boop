// boopservice.js
// Used to display notifications from boop.

self.addEventListener('notificationclick', function(event) {
    console.log(event)
    event.notification.close();
    event.waitUntil(clients.openWindow(event.notification.data.url));
});

self.addEventListener('push', function(event) {
    console.log(`Push data: "${event.data.text()}"`);
    options = JSON.parse(event.data.text())
    const title = options.title;
    options.requireInteraction = false;
    options.data = options

    event.waitUntil(self.registration.showNotification(title, options));
});
