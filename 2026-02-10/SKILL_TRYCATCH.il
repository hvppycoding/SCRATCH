/*******************************************************************************
* Macro: CaptureAll
* Description: Captures stdout, warnings, and errors into strings.
* Usage: CaptureAll( code... )
* Returns: list( OutputString WarningString ErrorString Result )
*******************************************************************************/
defmacro( CaptureAll (@rest body)
    `(let( (outP warnP errP res outS warnS errS)

        ; 1. Create string output ports (in-memory)
        outP = outstring()
        warnP = outstring()
        errP = outstring()

        ; 2. Redirect system ports (poport, woport, errport) to our ports
        let( ((poport outP) (woport warnP) (errport errP))
            
            ; 3. Execute the body safely using errset
            ;    The comma-at operator ( ,@ ) splices the body code here.
            res = errset( progn( ,@body ) t )
        )

        ; 4. Extract strings from ports
        outS = getOutstring(outP)
        warnS = getOutstring(warnP)
        errS = getOutstring(errP)

        ; 5. Close ports to free memory
        close(outP)
        close(warnP)
        close(errP)

        ; 6. Return the list of strings and the result
        list( outS warnS errS res )
    )
)




; --- Test Execution ---
result = CaptureAll(
    printf("1. This is standard output.\n")
    warn("2. This is a warning message.")
    printf("3. Calculating 10 / 0 ...\n")
    x = 10 / 0  ; This will cause an error
    printf("4. This line will not run.\n")
)

; --- Check Results ---
printf("\n=== RESULT ===\n")
printf("OUTPUT : %s\n" nth(0 result))
printf("WARNING: %s\n" nth(1 result))
printf("ERROR  : %s\n" nth(2 result))
printf("RETURN : %L\n" nth(3 result))



; --- Test Scenario ---
result = CaptureAll(
    printf("1. Start Testing...\n")

    ; [Test 1] Syntax Error (Simulated)
    ; We use 'evalstring' because if we type bad syntax directly, 
    ; the CIW reader stops before the macro runs.
    ; Below: Missing closing parenthesis ')'
    evalstring( "if( t then printf('This is bad syntax') " )
    
    ; Note: The script stops at the first error, 
    ; so lines below this will not run.
    printf("2. This line will NOT run.\n")
)

; --- Check Results ---
printf("\n=== RESULT ===\n")
printf("OUTPUT : %s\n" nth(0 result))
printf("WARNING: %s\n" nth(1 result))
printf("ERROR  : %s\n" nth(2 result)) 
printf("=====================\n")

