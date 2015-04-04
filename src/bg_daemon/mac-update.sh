#!/usr/bin/env bash
FN=${1}-temp.jpg
cp $1 $FN

if quack -h &>/dev/null; then
    # OSX will think it's the same image if they are named the same
    # so trick it into thinking it's a different one
    quack $FN
    quack $1
    rm $FN
else
    osascript<<EOF
    tell application "Finder"
        set desktop picture to POSIX file "$1"
    end tell
EOF

    # this is an ugly hack to force updating...
    killall Dock
fi

