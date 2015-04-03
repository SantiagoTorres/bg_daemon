#!/usr/bin/env bash
if quack -h &>/dev/null; then
    quack -i $1
else
    osascript<<EOF
    tell application "Finder"
        set desktop picture to POSIX file "$1"
    end tell
EOF

    # this is an ugly hack to force updating...
    killall Dock
fi

