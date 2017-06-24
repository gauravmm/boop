// boopservice.js
// Used to display notifications from boop.

self.addEventListener('push', function(event) {
    console.log('[Service Worker] Push Received.');
    console.log(`[Service Worker] Push had this data: "${event.data.text()}"`);

    const title = 'Push Codelab';
    const options = {
        body: 'Yay it works.',
    };

    self.addEventListener('notificationclick', function(event) {
        console.log('[Service Worker] Notification click Received.');
        event.notification.close();
        event.waitUntil(
            clients.openWindow('https://developers.google.com/web/')
        );
    });

    event.waitUntil(self.registration.showNotification(title, options));
});
