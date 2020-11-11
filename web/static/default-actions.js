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
            var select = document.getElementById('model-select');
            var stringContent = "";
            models.forEach(element => {
                stringContent += `<option value="${element}">${element}</option>`;
            });  
            select.innerHTML = stringContent;  
        } else {
            console.log(response);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });