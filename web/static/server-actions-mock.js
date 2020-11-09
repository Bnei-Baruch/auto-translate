function callCPUUsageInPercents() {
    var percentage = Math.floor(Math.random() * Math.floor(100));
    return new Promise(
        function (resolve, reject) {
                resolve({
                    ok: true,
                    json: function(){
                        return { cpu: percentage };
                    },
                }); 
        }
    );
}

function callProgressInPercents(id, number = null) {
    return new Promise(
        function (resolve, reject) {
                resolve({
                    ok: true,
                    json: function(){
                        return { progress: number };
                    },
                }); 
        }
    );
}

function callFileProcessing(file) {
    return fetch('/', {
        method: 'PUT',
        body: file
    });
}

function callTextProcessing(text) {
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

function callSaveAsTable(textInput, textOutput) {
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