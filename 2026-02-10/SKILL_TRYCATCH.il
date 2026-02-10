/*******************************************************************************
* Function: CaptureAll
* Description: Executes code and captures Stdout, Warnings, and Errors separately.
* Input: Quoted code list (e.g., '( printf(...) ) )
* Returns: list( "OutputString" "WarningString" "ErrorString" ExecutionResult )
*******************************************************************************/
procedure( CaptureAll( codeList )
    let( (outP warnP errP res outS warnS errS)
        
        ; 1. Create string output ports (in-memory streams)
        outP = outstring()
        warnP = outstring()
        errP = outstring()
        
        ; 2. Redirect standard system ports to our variable ports
        ; poport = Standard Output, woport = Warning Output, errport = Error Output
        let( ((poport outP) (woport warnP) (errport errP))
            
            ; 3. Execute code safely
            ; 't' ensures error messages are sent to our captured 'errport'
            res = errset( eval(codeList) t )
        )
        
        ; 4. Extract strings from ports
        outS = getOutstring(outP)
        warnS = getOutstring(warnP)
        errS = getOutstring(errP)
        
        ; 5. Close ports to free memory
        close(outP)
        close(warnP)
        close(errP)
        
        ; 6. Return the list
        list( outS warnS errS res )
    )
)



; --- Test Scenario ---
resultList = CaptureAll( '(
    progn(
        printf("1. Normal output message.\n")
        
        warn("2. This is a warning message!")
        
        printf("3. About to divide by zero...\n")
        
        ; This causes an error
        result = 10 / 0 
        
        printf("4. This line will NOT be executed.\n")
    )
) )

; --- Check Results ---
printf("\n=== CAPTURED LOGS ===\n")
printf("[OUTPUT] : \n%s\n" nth(0 resultList))
printf("[WARNING]: \n%s\n" nth(1 resultList))
printf("[ERROR]  : \n%s\n" nth(2 resultList))
printf("=====================\n")

