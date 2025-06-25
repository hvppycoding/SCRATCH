#!/bin/tcsh

# === Variables ===
set HOSTNAME = `hostname`
set USERNAME = $USER
set BASE_PROFILE = /user/$USERNAME/.config/google-chrome
set TMP_PROFILE = /tmp/${USERNAME}_chrome_profile_${HOSTNAME}

# === ANSI Colors ===
set COLOR_INFO = "\033[1;34m"      # Blue
set COLOR_WARN = "\033[1;33m"      # Yellow
set COLOR_DONE = "\033[1;32m"      # Green
set COLOR_RESET = "\033[0m"

# === Show Target Directory ===
echo "${COLOR_INFO}==> Chrome temporary profile path: $TMP_PROFILE${COLOR_RESET}"

# === If temp profile directory does not exist, copy from base ===
if (! -d "$TMP_PROFILE") then
    echo "${COLOR_WARN}==> Temporary directory does not exist. Creating and syncing base profile...${COLOR_RESET}"
    mkdir -p "$TMP_PROFILE"

    rsync -au \
        --exclude='/SingletonLock' \
        --exclude='/SingletonSocket' \
        --exclude='/SingletonCookie' \
        "$BASE_PROFILE/" "$TMP_PROFILE/"
else
    echo "${COLOR_INFO}==> Temporary directory already exists. Skipping initial sync.${COLOR_RESET}"
endif

# === Launch Chrome ===
echo "${COLOR_INFO}==> Launching Chrome with user data dir: $TMP_PROFILE${COLOR_RESET}"
google-chrome --user-data-dir="$TMP_PROFILE"

# === After Chrome exits, sync back changes ===
echo "${COLOR_WARN}==> Chrome exited. Syncing back changes to base profile...${COLOR_RESET}"
rsync -au \
    --exclude='/SingletonLock' \
    --exclude='/SingletonSocket' \
    --exclude='/SingletonCookie' \
    "$TMP_PROFILE/" "$BASE_PROFILE/"

echo "${COLOR_DONE}==> Done.${COLOR_RESET}"
