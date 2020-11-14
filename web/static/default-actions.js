setInterval(() => {
    callCPUUsageInPercents()
        .then(response => response.json())
        .then(response => {
            var percent = +response.cpu;
            setCPU(percent);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}, 1000)


callGetTranslateModels()
    .then(response => response.json())
    .then(response => {
        var models = response.models;
        var objects = models.map(el => {
            var parts = el.split('_');
            return {
                srcLang: parts[0],
                destLang: parts[1],
                style: parts[2],
                version: parts[3],
                date: parts[4]
            }
        })
        window.translateModels = objects;
        modelSelectChanged();
    })
    .catch(error => {
        console.error('Error:', error);
    });

