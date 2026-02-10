defmacro( CaptureAll (@rest body)
    `(let( ((outP outstring()) (warnP outstring()) (errP outstring()) result)
        
        unwindProtect(
            ;-----------------------------------------------------------
            ; [Main Block] 실행 및 캡처
            ;-----------------------------------------------------------
            {
                let( ((poport outP) (woport warnP) (errport errP))
                    
                    ; 1. 코드 실행
                    result = errset( progn( ,@body ) t )

                    ; 2. 요청하신 강제 플러싱 및 getWarn 호출
                    warn("")   
                    getWarn()  ; 여기서 호출하면 warnP의 내용이 한번 비워집니다.
                )

                ; 3. 결과 리턴 (getWarn으로 비워진 후 새로 쌓인 게 있다면 가져옴)
                list( getOutstring(outP) getOutstring(warnP) getOutstring(errP) result )
            }

            ;-----------------------------------------------------------
            ; [Cleanup Block] 포트 정리 (에러가 나도 무조건 실행)
            ;-----------------------------------------------------------
            {
                close(outP) 
                close(warnP) 
                close(errP)
            }
        )
    )
)





; --- Test 1: Standard Output, Warning, and Runtime Error ---
printf("\n--- TEST 1: General Logic ---\n")
result1 = CaptureAll(
    printf("1. Normal Output.\n")
    warn("2. Warning Message.")
    
    ; Runtime Error (Division by zero)
    x = 10 / 0 
    
    printf("3. This line is skipped.\n")
)

printf("OUT : %s\n" nth(0 result1))
printf("WARN: %s\n" nth(1 result1))
printf("ERR : %s\n" nth(2 result1))


; --- Test 2: Syntax Error Capture ---
printf("\n--- TEST 2: Syntax Error (via evalstring) ---\n")
result2 = CaptureAll(
    printf("1. Trying to run bad syntax...\n")
    
    ; We use evalstring to simulate a syntax error (missing closing parenthesis)
    evalstring(" if( t then printf('Missing Paren') ")
)

printf("OUT : %s\n" nth(0 result2))
printf("ERR : %s\n" nth(2 result2)) 
; You should see *Error* syntax error in the ERR output.
