---
name: ios-remote-install
description: Install an iOS build on a physical iPhone that is not on the local network — over Tailscale, TestFlight, or a cable — when Xcode's own wireless install cannot reach the device. Use when asked to push, deploy, update, or sideload an app to a phone that is away, travelling, in another state, or otherwise unreachable, or when devicectl reports a paired device as unavailable.
---

# Installing on an iPhone that is somewhere else

Apple's wireless install finds devices with **mDNS on the local link**. Tailscale
carries IP but not multicast, so `xcrun devicectl` cannot see a phone on the
tailnet no matter how well it pings. This is the workaround, and the reason it
works: **iOS installs any signed build from an HTTPS URL it trusts**, and
`tailscale serve` provides one with a real certificate.

## First, confirm which problem you have

```
xcrun devicectl list devices
```

`available` means the phone is reachable — just use `xcrun devicectl device
install app --device <UDID> <path>.app` and stop reading. `unavailable` on a
`paired` device means it is not on this network; continue.

```
tailscale status | grep -i iphone
```

If the phone is on the tailnet, the OTA route below works. If it is not, only
TestFlight or a cable will do it.

## The requirement people miss

**The phone's UDID must already be in the provisioning profile.** A development
build installs only on devices listed in its profile, and a phone gets listed by
being plugged in once. Check before building anything, because the failure
otherwise appears at the very last step:

```
unzip -q Payload.ipa && security cms -D -i Payload/*.app/embedded.mobileprovision > prof.plist
/usr/libexec/PlistBuddy -c "Print :ProvisionedDevices" prof.plist | grep -i <device-udid>
```

No match means stop: no amount of serving will install it.

## The procedure

**1. Archive and export a development-signed IPA.** For Xcode 15.3+ the export
method is `debugging` (older Xcode calls it `development`):

```
xcodebuild -project App.xcodeproj -scheme App -configuration Release \
  -destination 'generic/platform=iOS' -archivePath /tmp/ota/App.xcarchive \
  DEVELOPMENT_TEAM=<TEAM> -allowProvisioningUpdates archive

xcodebuild -exportArchive -archivePath /tmp/ota/App.xcarchive \
  -exportOptionsPlist /tmp/ota/export.plist -exportPath /tmp/ota/export \
  -allowProvisioningUpdates
```

with `export.plist` carrying `method=debugging`, `teamID`, `signingStyle=automatic`,
and `thinning=<none>` — thinning produces per-device assets the manifest cannot
name.

Read the team id out of the keychain rather than hard-coding it, so the recipe
survives a second machine:

```
security find-certificate -c "Apple Development" -p | openssl x509 -noout -subject \
  | grep -oE 'OU=[A-Z0-9]+' | cut -d= -f2
```

**2. Write an `itms-services` manifest.** A plist naming the IPA's HTTPS URL,
the bundle id, the version, and a title. Both URLs — manifest and IPA — must be
HTTPS with a certificate iOS already trusts. Lint it (`plutil -lint`); a
malformed manifest fails on the phone with no useful message.

**3. Serve it over the tailnet.**

```
tailscale status --json | python3 -c 'import json,sys; print(json.load(sys.stdin)["Self"]["DNSName"].rstrip("."))'
```

That name has a real cert. Two traps:

- **macOS Tailscale cannot serve files.** The App Store build is sandboxed and
  refuses `--set-path <dir>`. Run a local file server and PROXY to it:
  `python3 -m http.server 8791 --bind 127.0.0.1` then
  `tailscale serve --bg --set-path /install http://127.0.0.1:8791`.
- **Check for an existing serve config first** (`tailscale serve status`).
  Publishing at `/` clobbers whatever is already there. Always mount on a path.

**4. Send a link, not instructions.** Serve a one-tap page:

```html
<a href="itms-services://?action=download-manifest&url=https://HOST/install/manifest.plist">Install</a>
```

The `itms-services:` scheme only works from Safari on the device. Sending the
manifest URL directly does nothing useful.

**5. Tear it down.** `tailscale serve --set-path /install off` and stop the file
server. Until then a signed build of the app is readable by anything on the
tailnet.

## When to reach for TestFlight instead

TestFlight is right when builds must reach **other people**, or a device you
cannot get a UDID for, or you want installs to keep working after the
development profile expires (7 days on a free team, a year on a paid one). It
costs an App Store Connect app record, an API key or app-specific password,
export-compliance answers, and a processing wait — and most of that is in
Apple's web UI, which an agent cannot do for someone. For one build onto one
known phone, the tailnet route is faster and needs no credential.

## Verify before claiming success

Fetch all three URLs and check the certificate actually validates:

```
curl -s -o /dev/null -w "%{http_code} %{ssl_verify_result}\n" https://HOST/install/manifest.plist
```

`ssl_verify_result=0` is the one that matters — iOS refuses a manifest served
under a certificate it does not trust, and a self-signed cert or a plain-HTTP
URL fails silently on the phone.

Then say plainly that the install itself is unverified until the person taps it.
You cannot see their home screen.
