#!/bin/tcsh
#BSUB -J chrome_job
#BSUB -o chrome_job.out
#BSUB -e chrome_job.err

# 변수 정의
set HOSTNAME = `hostname`
set USERNAME = $USER
set BASE_PROFILE = /user/$USERNAME/.config/google-chrome
set TMP_PROFILE = /tmp/${USERNAME}_chrome_profile_${HOSTNAME}

echo "===> Chrome 임시 프로필 경로: $TMP_PROFILE"

# 폴더가 존재하지 않으면 초기 복사 수행
if (! -d "$TMP_PROFILE") then
    echo "===> 임시 폴더가 없어 생성합니다."
    mkdir -p "$TMP_PROFILE"

    echo "===> 초기 rsync 복사 시작..."
    rsync -au \
        --exclude='/SingletonLock' \
        --exclude='/SingletonSocket' \
        --exclude='/SingletonCookie' \
        "$BASE_PROFILE/" "$TMP_PROFILE/"
else
    echo "===> 기존 임시 폴더가 존재하므로 복사하지 않음."
endif

# Chrome 실행
echo "===> Chrome 실행 시작..."
google-chrome --user-data-dir="$TMP_PROFILE"

# Chrome 종료 후 변경 사항 반영
echo "===> Chrome 종료됨. 변경사항 동기화 중..."
rsync -au \
    --exclude='/SingletonLock' \
    --exclude='/SingletonSocket' \
    --exclude='/SingletonCookie' \
    "$TMP_PROFILE/" "$BASE_PROFILE/"

echo "===> 작업 완료."
