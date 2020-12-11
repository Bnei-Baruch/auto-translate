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

    var data = {
        text: text
    };

    return fetch(`/text?timestamp=${timestamp}&model=${model}`, {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
    });
}

function callSaveAsTable(textInput, textOutput, timestamp, model) {

    var data = {
        textInput: textInput,
        textOutput: textOutput
    };

    return fetch(`/save-as-table?timestamp=${timestamp}&model=${model}`, {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
    });
}

function callGetTranslateModels() {
    return fetch('/translate-models', {
        method: 'GET'
    });
}