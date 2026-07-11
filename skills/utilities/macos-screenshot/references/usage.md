# Usage

```sh
bin/macos-screenshot check
bin/macos-screenshot capture --output /tmp/screen.png --display 1
bin/macos-screenshot capture --output /tmp/region.png --region 100,100,800,600
bin/macos-screenshot capture --output /tmp/window.png --window-id 12345
bin/macos-screenshot capture --output /tmp/selection.png --interactive
```

The host application may need Screen & System Audio Recording permission under macOS Privacy & Security. Interactive capture hands selection to the user. Region values are `x,y,width,height`.

The tool uses native `/usr/sbin/screencapture`, suppresses camera-shutter audio, and writes PNG.

