// boopservice.js
// Used to display notifications from boop.

self.addEventListener('push', function(event) {
    console.log('[Service Worker] Push Received.');
    console.log(`[Service Worker] Push had this data: "${event.data.text()}"`);

    const title = 'Boop Notification';
    const options = {
        body: event.data.text()
    };

    self.addEventListener('notificationclick', function(event) {
        console.log('[Service Worker] Notification click Received.');
        event.notification.close();
        event.waitUntil(clients.openWindow('google.com'));
    });

    event.waitUntil(self.registration.showNotification(title, options));
});
