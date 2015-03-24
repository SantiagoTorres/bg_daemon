#!/usr/bin/env bash
osascript<<EOF
tell applcation "Finder"
    set desktop picture to POSIX file "$1"
end tell
EOF

# this is an ugly hack to force updating...
killall Dock
