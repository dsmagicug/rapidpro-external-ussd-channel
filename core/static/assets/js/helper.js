function standardShortcode(code){
    const newCode = code.toString();
    const ln = newCode.length;
    let start = "";
    let end = ""
    let final = newCode;
    if(newCode[0] !== "*" & newCode[ln-1] !== "#"){
        start = "*";
        end = "#";
        final = start+newCode+end
    }
    return final
}