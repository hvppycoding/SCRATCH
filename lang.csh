if (! $?LANG) then
    echo "[INFO] LANG not set. Defaulting to ko_KR.UTF-8"
    setenv LANG ko_KR.UTF-8
else
    switch ("$LANG")
        case en*:
            setenv LANG en_US.UTF-8
            breaksw
        case ko*:
            setenv LANG ko_KR.UTF-8
            breaksw
        case C:
        case POSIX:
            echo "[INFO] LANG is $LANG — upgrading to en_US.UTF-8 for UTF-8 support"
            setenv LANG en_US.UTF-8
            breaksw
        default:
            echo "[INFO] Unrecognized LANG: $LANG. Defaulting to en_US.UTF-8"
            setenv LANG en_US.UTF-8
            breaksw
    endsw
endif
