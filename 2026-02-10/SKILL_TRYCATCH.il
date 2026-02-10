(defmacro CaptureAll (@rest body)
    `(let ( (outP (outstring)) 
            (warnP (outstring)) 
            (errP (outstring)) 
            (res nil)
            outS warnS errS )
        
        ; 1. 포트 가로채기 (let 바인딩 괄호 주의)
        (let ( (poport outP) (woport warnP) (errport errP) )
            
            ; 2. 코드 실행 (Comma-at ,@ 사용)
            (setq res (errset (progn ,@body) t))
        )
        
        ; 3. 결과 추출
        (setq outS (getOutstring outP))
        (setq warnS (getOutstring warnP))
        (setq errS (getOutstring errP))
        
        ; 4. 정리
        (close outP) (close warnP) (close errP)
        
        ; 5. 리턴
        (list outS warnS errS res)
    )
)


; [테스트]
result = CaptureAll(
    printf("1. 아웃풋 테스트\n")
    warn("2. 워닝 테스트")
    x = 10 / 0  ; 3. 에러 테스트
)

; [결과 확인]
printf("OUT : %s\n" nth(0 result))
printf("WARN: %s\n" nth(1 result))
printf("ERR : %s\n" nth(2 result))
