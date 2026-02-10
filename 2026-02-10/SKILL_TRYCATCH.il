procedure( CaptureAllString( codeString )
    let( (outP warnP errP result outS warnS errS)
        
        ; 1. Create Ports
        outP = outstring()
        warnP = outstring()
        errP = outstring()

        unwindProtect(
            ;-----------------------------------------------------------
            ; [Main Block]
            ;-----------------------------------------------------------
            {
                let( ((poport outP) (woport warnP) (errport errP))
                    
                    ; Execute the string using 'evalstring'
                    result = errset( evalstring(codeString) t )

                    ; Force flush & call getWarn as requested
                    warn("")
                    getWarn() 
                )

                ; Capture final strings from ports
                outS = getOutstring(outP)
                warnS = getOutstring(warnP)
                errS = getOutstring(errP)

                ; Return list
                list( outS warnS errS result )
            }
            
            ;-----------------------------------------------------------
            ; [Cleanup Block]
            ;-----------------------------------------------------------
            {
                close(outP) 
                close(warnP) 
                close(errP)
            }
        )
    )
)





; --- 테스트 코드 ---
code = "
    printf('Start_Test...')
    
    warn('This is a warning inside string')
    
    x = 10
    y = 0
    
    ; 에러 발생 코드
    z = x / y
"

; 함수 호출
result = CaptureAllString( code )

; --- 결과 확인 ---
printf(\"OUTPUT : %s\\n\" nth(0 result))
printf(\"WARN   : %s\\n\" nth(1 result))
printf(\"ERROR  : %s\\n\" nth(2 result))
