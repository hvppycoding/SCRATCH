defmacro( CaptureAll (@rest body)
    `(let( (outP warnP errP result outS warnS errS)
        
        ; 1. Create string ports for all 3 channels
        outP = outstring()
        warnP = outstring()
        errP = outstring()

        unwindProtect(
            ;-----------------------------------------------------------
            ; main clause - redirect output, warning, and error ports
            ;-----------------------------------------------------------
            {
                let( ((poport outP) (woport warnP) (errport errP))
                    
                    ; Execute body safely using errset to catch errors
                    result = errset( progn( ,@body ) t )

                    ; Force final warning to be flushed (as requested)
                    warn("")
                    
                    ; Note: If 'getWarn()' is a custom function in your env, 
                    ; it would be called here. Standard SKILL uses getOutstring below.
                )
                
                ;-------------------------------------------------------
                ; Capture data from ports into strings
                ;-------------------------------------------------------
                outS = getOutstring(outP)
                warnS = getOutstring(warnP)
                errS = getOutstring(errP)
                
                ; Return all captured data and the execution result
                list( outS warnS errS result )
            }
            
            ;-----------------------------------------------------------
            ; cleanup clause - always close ports to prevent memory leaks
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
