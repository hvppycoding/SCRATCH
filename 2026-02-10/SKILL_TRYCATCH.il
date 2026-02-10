/*******************************************************************************
* 기능: 코드 블록을 실행하고 stdout, warning, error 메시지를 분리해서 리턴
* 리턴값: list( "Output문자열" "Warning문자열" "Error문자열" 실행결과 )
*******************************************************************************/
defmacro( CaptureAll (@rest body)
    `(let( (outPort warnPort errPort result outputStr warnStr errStr)
        
        ; 1. 3개의 가상 스트림(메모리) 생성
        outPort  = makeStringOutputStream()
        warnPort = makeStringOutputStream()
        errPort  = makeStringOutputStream()
        
        ; 2. 3대 포트(poport, woport, errport)를 모두 가상 포트로 납치(Redirection)
        let( ((poport outPort) (woport warnPort) (errport errPort))
            
            ; 3. 코드 실행 (errset으로 감싸서 에러가 나도 죽지 않게 함)
            ;    errset의 두 번째 인자 t는 "에러 메시지를 출력하라"는 뜻인데,
            ;    우리가 errport를 납치했으므로 화면이 아닌 errPort 변수에 담깁니다.
            result = errset( progn( ,@body ) t )
        )
        
        ; 4. 각 포트에 담긴 내용을 문자열로 변환
        outputStr = getOutstring(outPort)
        warnStr   = getOutstring(warnPort)
        errStr    = getOutstring(errPort)
        
        ; 포트 닫기 (메모리 정리)
        close(outPort)
        close(warnPort)
        close(errPort)
        
        ; 5. 결과 리턴 (리스트 형태)
        ; result는 errset의 결과이므로 (값) 형태의 리스트거나 nil(에러시)입니다.
        list( outputStr warnStr errStr result )
    )
)




; --- 테스트 시나리오 ---
; 1. 일반 출력 (printf)
; 2. 경고 발생 (warn)
; 3. 에러 발생 (10 / 0)

data = CaptureAll(
    printf("1. 지금부터 계산을 시작합니다.\n")
    x = 100
    y = 0
    
    warn("2. 주의하세요! y값이 0인 것 같습니다.")
    
    printf("3. 나누기를 시도합니다...\n")
    z = x / y  ; 여기서 에러 발생!
    
    printf("4. 이 메시지는 에러 때문에 실행되지 않습니다.\n")
)

; --- 결과 확인 및 파싱 ---
; data 변수에는 ("아웃풋" "워닝" "에러" 결과) 순서로 들어있습니다.

outputMsg = nth(0 data)
warnMsg   = nth(1 data)
errMsg    = nth(2 data)
execRes   = nth(3 data)

printf("=============================\n")
printf("[내용 1] 일반 출력:\n%s\n" outputMsg)
printf("-----------------------------\n")
printf("[내용 2] 경고 메시지:\n%s\n" warnMsg)
printf("-----------------------------\n")
printf("[내용 3] 에러 메시지:\n%s\n" errMsg)
printf("=============================\n")

if( execRes then
    printf("실행 결과: 성공 (%L)\n" car(execRes))
else
    printf("실행 결과: 실패 (nil)\n")
)




