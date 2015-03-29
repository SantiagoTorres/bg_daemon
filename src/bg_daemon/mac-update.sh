#!/usr/bin/env bash
osascript<<EOF
tell application "Finder"
    set desktop picture to POSIX file "$1"
end tell
EOF

# this is an ugly hack to force updating...
killall Dock
