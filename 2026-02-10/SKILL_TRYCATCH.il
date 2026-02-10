/*******************************************************************************
* 함수명: CaptureAll
* 사용법: CaptureAll( '( 코드... ) )
* 리턴값: list( "Output" "Warning" "Error" 결과 )
*******************************************************************************/
procedure( CaptureAll( codeList )
    let( (outP warnP errP res outS warnS errS)
        
        ; 1. 메모리 포트 생성 (함수명 수정: makeStringOutputStream -> outstring)
        outP = outstring()
        warnP = outstring()
        errP = outstring()
        
        ; 2. 3대 포트 가로채기 (poport, woport, errport)
        let( ((poport outP) (woport warnP) (errport errP))
            ; 코드 실행 (에러 발생 시에도 멈추지 않음)
            res = errset( eval(codeList) t )
        )
        
        ; 3. 포트에 담긴 문자열 꺼내기
        outS = getOutstring(outP)
        warnS = getOutstring(warnP)
        errS = getOutstring(errP)
        
        ; 4. 포트 닫기
        close(outP)
        close(warnP)
        close(errP)
        
        ; 5. 결과 리턴
        list( outS warnS errS res )
    )
)



; --- 테스트 코드 ---
resultList = CaptureAll( '(
    progn(
        printf("1. 일반 출력 메시지입니다.\n")
        warn("2. 이것은 경고(Warning) 메시지입니다.")
        printf("3. 에러 발생 직전...\n")
        x = 10 / 0  ; 에러 발생!
        printf("4. 이 줄은 실행되지 않습니다.\n")
    )
) )

; --- 결과 확인 ---
printf("==================================\n")
printf("[Output]  : %s\n" nth(0 resultList))
printf("[Warning] : %s\n" nth(1 resultList))
printf("[Error]   : %s\n" nth(2 resultList))
printf("==================================\n")
