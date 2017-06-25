# BOOP
Scriptable browser push notifications. Like pushover, but self-run.

![boop screenshot](http://i.imgur.com/UrKMtHz.png "Screenshot")

## How it Works

We support notifications from mulitple sources to multiple sinks. A sink is any browser or mobile OS that supports the HTML5 WebPush standard, and a source is any device that can make an HTTP request.

We ship this with a script already written for `bash`. To display a notification, all you need to do from a source device is:

```
boop "Title" "Longer text content that can take up more than one line."
``` 

This makes a notification appear on every sink device. Here's what this looks like with Chrome on Ubuntu:

![boop notification](http://i.imgur.com/DCFVN4r.png "Notification")

Naturally, sending notifications is easy to use, and completely scriptable.

## How to Use

 1. Install the prerequisites:
```
# Consider creating a virtualenv
sudo apt-get install python3 python3-pip python3-dev libffi-dev libssl-dev
pip install --upgrade pip # pip3 9.0+ is required
pip install git+https://github.com/web-push-libs/vapid.git#subdirectory=python
pip install pywebpush
```
 2. Download the software on a computer accessible to your source devices. This can be your desktop (for the local network) or a server.
 3. Edit `config.py` and change authentication settings, server URL, and port.
 4. Run it with the script `./boop`. The first time it is run, secret keys are automatically generated.
 5. On any device, open a browser and point it at the server. You can register devices as sources and sinks right in this interface.

When you add a source, a unique authentication key allows you to push notifications without storing your password natively. You can revoke these keys anytime.

## Code

### Security

The web interface should only be accessible  through an SSH proxy because your login information is sent in plaintext.

The push interface can be safely used in plaintext. Your secret is never transmitted;instead, a timestamp and the exact message are concatenated to the secret key before being hashed. These keys can also be individually revoked through the web interface.

### To-do

 1. The massive empty space in the interface should be used to display past notifications. We don't have to store these on disk, just keep ~100 in memory.
 2. Better disk storage, not simple pickle-based disk dumps.
 3. Allow for push options like automatic replacement, persistent, and options.
 4. Testing
