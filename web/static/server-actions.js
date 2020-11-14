function callCPUUsageInPercents() {
    return fetch(`/cpu`, {
        method: 'GET'
    });
}

function callProgressInPercents(timestamp) {
    return fetch(`/progress?timestamp=${timestamp}`, {
        method: 'GET'
    });
}

function callFileProcessing(file, timestamp, model) {
    return fetch(`/upload?timestamp=${timestamp}&model=${model}`, {
        method: 'PUT',
        body: file
    });
}

function callTextProcessing(text, timestamp, model) {

    return fetch(`/text?timestamp=${timestamp}&model=${model}`, {
        method: 'POST',
        body: {
            text: text
        },
        headers: {
            'Content-Type': 'application/json'
        },
    });
}

function callSaveAsTable(textInput, textOutput, model) {
    return fetch(`/save-as-table?timestamp=${timestamp}&model=${model}`, {
        method: 'POST',
        body: {
            textInput: textInput,
            textOutput: textOutput
        },
        headers: {
            'Content-Type': 'application/json'
        },
    });
}

function callGetTranslateModels() {
    return fetch('/translate-models', {
        method: 'GET'
    });
}