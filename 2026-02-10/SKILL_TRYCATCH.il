/*******************************************************************************
* Macro: CaptureAll
* Style: S-Expression (Lisp-style) to prevent parser errors.
* Usage: CaptureAll( code... )
* Returns: list( OutputString WarningString ErrorString Result )
*******************************************************************************/
(defmacro CaptureAll (@rest body)
    `(let ( (outP (outstring)) 
            (warnP (outstring)) 
            (errP (outstring)) 
            (res nil)
            outS warnS errS )
        
        ; 1. Redirect standard ports (poport, woport, errport)
        (let ( (poport outP) (woport warnP) (errport errP) )
            
            ; 2. Execute code safely
            ;    (progn ,@body) groups multiple lines into one block
            (setq res (errset (progn ,@body) t))
        )
        
        ; 3. Extract strings from ports
        (setq outS (getOutstring outP))
        (setq warnS (getOutstring warnP))
        (setq errS (getOutstring errP))
        
        ; 4. Cleanup (Close ports)
        (close outP) (close warnP) (close errP)
        
        ; 5. Return the list
        (list outS warnS errS res)
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
