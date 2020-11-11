setInterval(() => {
    callCPUUsageInPercents()
        .then(response => {
            if (response.ok) {
                var percent = +response.json().cpu;
                setCPU(percent);
            } else {
                console.error(response);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}, 1000)

callGetTranslateModels()
    .then(response => {
        if (response.ok) {
            var models = response.json().models;
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
        } else {
            console.log(response);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });

