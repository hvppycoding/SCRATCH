procedure( CaptureAllFunc( codeToRun )
    let( (outP warnP errP res outS warnS errS)
        outP = makeStringOutputStream()
        warnP = makeStringOutputStream()
        errP = makeStringOutputStream()
        
        let( ((poport outP) (woport warnP) (errport errP))
            ; eval을 사용하여 실행합니다.
            res = errset( eval(codeToRun) t )
        )
        
        outS = getOutstring(outP)
        warnS = getOutstring(warnP)
        errS = getOutstring(errP)
        close(outP) close(warnP) close(errP)
        
        list( outS warnS errS res )
    )
)



; 사용법: CaptureAllFunc( '( 코드... ) )
result = CaptureAllFunc( '(
    printf("Test Output\n")
    warn("Test Warning")
    10 / 0
) )
