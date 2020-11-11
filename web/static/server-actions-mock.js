function callCPUUsageInPercents() {
    var percentage = Math.floor(Math.random() * Math.floor(100));
    return new Promise(
        function (resolve, reject) {
            resolve({
                ok: true,
                json: function () {
                    return {
                        cpu: percentage
                    };
                },
            });
        }
    );
}

function callProgressInPercents(timestamp, number = null) {
    return new Promise(
        function (resolve, reject) {
            resolve({
                ok: true,
                json: function () {
                    return {
                        progress: number
                    };
                },
            });
        }
    );
}

function callFileProcessing(file, timestamp, model) {
    return fetch('/', {
        method: 'PUT',
        body: file
    });
}

function callTextProcessing(text, timestamp, model) {
    return new Promise(
        function (resolve, reject) {
            resolve({
                ok: true,
                json: function () {
                    return {
                        sourceText: text,
                        translatedText: "translated text"
                    };
                },
            });
        }
    );
}

function callSaveAsTable(textInput, textOutput, model) {
    return fetch('/save-as-table', {
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
    return new Promise(
        function (resolve, reject) {
            resolve({
                ok: true,
                json: function () {
                    return {
                        models: [
                            'he_en_zohar_V17_nov-5-20',
                            'he_en_zohar_V09_apr-5-19',
                            'he_es_zohar_V05_oct-13-20'
                        ]
                    };
                },
            });
        }
    );
}