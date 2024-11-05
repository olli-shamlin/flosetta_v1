
function trace(msg, caller_name=null) {
    if (trace_switch) {
        if (caller_name == null) { caller_name = trace.caller.name }
        console.log(`[ROSETTA ➤ ${caller_name}] ${msg}`)
    }
}

function traceEnter(caller_name=null) {
    if (trace_switch) {
        if (caller_name == null) { caller_name = traceEnter.caller.name }
        console.log(`[ROSETTA ➤ ${caller_name}] ↪︎ enter`)
    }
}

function traceExit(caller_name=null) {
    if (trace_switch) {
        if (caller_name == null) { caller_name = traceExit.caller.name }
        console.log(`[ROSETTA ➤ ${caller_name}] ↩︎ exit`)
    }
}

function traceFatal(msg, caller_name=null) {
    if (trace_switch) {
        if (caller_name == null) { caller_name = traceFatal.caller.name }
        console.log(`[ROSETTA ➤ ${caller_name}] FATAL ERROR: ${msg}`)
    }
    alert('FATAL ERROR: ' + msg)
}
