function callCPUUsageInPercents(){
   return fetch('/cpu', {
        method: 'GET'
    });
}

function callProgressInPercents(){
    return fetch('/progress', {
        method: 'GET'
    });
}

function callFileProcessing(file){
    return fetch('/', {
        method: 'PUT',
        body: file
    });
}

function callTextProcessing(text){
    return fetch('/text', {
        method: 'POST',
        body: {
            text: text,
            sourceLang: 'he',
            destinationLang: 'en',
            version: 'some string'
        },
        headers: {
            'Content-Type': 'application/json'
        },
    });
}

function callSaveAsTable(textInput, textOutput){
    return fetch('/save-as-table', {
        method: 'POST',
        body: {
            textInput: textInput,
            textOutput: textOutput,
            sourceLang: 'he',
            destinationLang: 'en',
            version: 'some string'
        },
        headers: {
            'Content-Type': 'application/json'
        },
    });
}