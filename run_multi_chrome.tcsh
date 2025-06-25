#!/bin/tcsh

# === Variables ===
set HOSTNAME = `hostname`
set USERNAME = $USER
set BASE_PROFILE = /user/$USERNAME/.config/google-chrome
set TMP_PROFILE = /tmp/${USERNAME}_chrome_profile_${HOSTNAME}

# === ANSI Colors ===
set COLOR_INFO = "\033[1;34m"
set COLOR_WARN = "\033[1;33m"
set COLOR_ERROR = "\033[1;31m"
set COLOR_DONE = "\033[1;32m"
set COLOR_RESET = "\033[0m"

echo "${COLOR_INFO}==> Chrome temporary profile path: $TMP_PROFILE${COLOR_RESET}"

# === Check if base profile exists ===
if (! -d "$BASE_PROFILE") then
    echo "${COLOR_WARN}==> WARNING: Base profile directory not found: $BASE_PROFILE"
    echo "    Skipping initial sync.${COLOR_RESET}"
else
    # === Copy base profile if temp profile doesn't exist ===
    if (! -d "$TMP_PROFILE") then
        echo "${COLOR_INFO}==> Creating temporary directory and syncing from base...${COLOR_RESET}"
        mkdir -p "$TMP_PROFILE"

        rsync -au \
            --exclude='/SingletonLock' \
            --exclude='/SingletonSocket' \
            --exclude='/SingletonCookie' \
            "$BASE_PROFILE/" "$TMP_PROFILE/"
    else
        echo "${COLOR_INFO}==> Temporary directory already exists. Skipping initial sync.${COLOR_RESET}"
    endif
endif

# === Launch Chrome ===
echo "${COLOR_INFO}==> Launching Chrome with user data dir: $TMP_PROFILE${COLOR_RESET}"
google-chrome --user-data-dir="$TMP_PROFILE"

# === Sync back to base if base exists ===
if (-d "$BASE_PROFILE") then
    echo "${COLOR_INFO}==> Chrome exited. Syncing changes back to base profile...${COLOR_RESET}"
    rsync -au \
        --exclude='/SingletonLock' \
        --exclude='/SingletonSocket' \
        --exclude='/SingletonCookie' \
        "$TMP_PROFILE/" "$BASE_PROFILE/"
else
    echo "${COLOR_WARN}==> Skipping sync back: base profile directory still does not exist.${COLOR_RESET}"
endif

echo "${COLOR_DONE}==> Done.${COLOR_RESET}"
