function showProgress(percent) {
    percent = percent > 100 ? 100 : percent;
    var scrollPercent = percent + "%";
    var element = document.getElementsByClassName("progress")[0];
    element.style.setProperty("display", 'block');

    var inner = element.getElementsByClassName("inner-progress")[0];
    inner.style.setProperty("width", scrollPercent);

    var span = element.getElementsByTagName("span")[0];
    span.innerHTML = scrollPercent;
}

function hideProgress() {
    var element = document.getElementsByClassName("progress")[0];
    element.style.setProperty("display", 'none');
    var span = element.getElementsByTagName("span")[0];
    span.innerHTML = null;
}

function blockInput() {

    var fromFileBtn = document.getElementById("fileload-btn");
    fromFileBtn.disabled = true;

    var sendFromTextBtn = document.getElementById("send-text-for-translation");
    sendFromTextBtn.disabled = true;

    var input = document.getElementById("input");
    input.setAttribute("contenteditable", false);

}

function unblockInput() {

    var fromFileBtn = document.getElementById("fileload-btn");
    fromFileBtn.disabled = false;

    var sendFromTextBtn = document.getElementById("send-text-for-translation");
    sendFromTextBtn.disabled = false;

    var input = document.getElementById("input");
    input.setAttribute("contenteditable", true);

}

function setCPU(percent) {

    var color = '#9ACD32';
    if (percent > 70) {
        color = 'red';
    } else if (percent > 30) {
        color = 'gold';
    }

    var cpu = document.getElementById("cpu");
    cpu.style.setProperty("display", 'block');
    cpu.style.borderColor = color;

    var cpuSpan = document.getElementById("cpu-span");
    cpuSpan.innerHTML = percent + '%';
    cpu.style.setProperty("color", color);
}

function getSelectedTranslateModel() {

    var srcLangSelect = document.getElementById('select-src-lg');
    var selectedSrcLang = getSelectValue(srcLangSelect);

    var destLangSelect = document.getElementById('select-dest-lg');
    var selectedDestLang = getSelectValue(destLangSelect);

    var styleSelect = document.getElementById('select-style');
    var selectedStyle = getSelectValue(styleSelect);

    var selectVersion = document.getElementById('select-version');
    var selectedVersion = getSelectValue(selectVersion);

    return `${selectedSrcLang}_${selectedDestLang}_${selectedStyle}_${selectedVersion}_nov-5-20`

}

function getTimestamp() {
    return new Date().getTime();
}

function getSelectValue(select) {

    if (select.selectedIndex < 0) {
        return null;
    }

    var selectedOption = select.options[select.selectedIndex];
    if (!selectedOption) {
        return null;
    }

    return selectedOption.value;
}

function modelSelectChanged() {

    var models = window.translateModels;
    if (!(models && models.length))
        return;

    var srcLangSelect = document.getElementById('select-src-lg');
    var selectedSrcLang = getSelectValue(srcLangSelect);

    srcLangSelect.innerHTML = models
        .map(el => el.srcLang)
        .filter((v, i, a) => a.indexOf(v) === i)
        .map((element, i) => {
            var selected = selectedSrcLang == element ? 'selected' : '';
            return `<option value="${element}" ${selected}>${element}</option>`;
        }).join("");

    if (selectedSrcLang !== null) {
        models = models.filter(m => m.srcLang === getSelectValue(srcLangSelect));
    }

    var destLangSelect = document.getElementById('select-dest-lg');
    var selectedDestLang = getSelectValue(destLangSelect);

    destLangSelect.innerHTML = models
        .map(el => el.destLang)
        .filter((v, i, a) => a.indexOf(v) === i)
        .map((element, i) => {
            var selected = selectedDestLang == element ? 'selected' : '';
            return `<option value="${element}" ${selected}>${element}</option>`;
        }).join("");

    if (selectedDestLang !== null) {
        models = models.filter(m => m.destLang === getSelectValue(destLangSelect));
    }

    var styleSelect = document.getElementById('select-style');
    var selectedStyle = getSelectValue(styleSelect);

    styleSelect.innerHTML = models
        .map(el => el.style)
        .filter((v, i, a) => a.indexOf(v) === i)
        .map((element, i) => {
            var selected = selectedStyle == element ? 'selected' : '';
            return `<option value="${element}" ${selected}>${element}</option>`;
        }).join("");

    if (selectedStyle !== null) {
        models = models.filter(m => m.style === getSelectValue(styleSelect));
    }

    var selectVersion = document.getElementById('select-version');
    var selectedVersion = getSelectValue(selectVersion);

    selectVersion.innerHTML = models
        .map(el => el.version)
        .filter((v, i, a) => a.indexOf(v) === i)
        .map((element, i) => {
            var selected = selectVersion == element ? 'selected' : '';
            return `<option value="${element}" ${selected}>${element}</option>`;
        }).join("");

    if (selectedVersion !== null) {
        models = models.filter(m => m.version === getSelectValue(selectVersion));
    }

}

function auto_grow(element) {
    element.style.height = "5px";
    element.style.height = (element.scrollHeight) + "px";
}

function setTexts(sourceTexts, destText) {

    const input = document.getElementById("input");
    const edited = document.getElementById("edited");

    edited.innerHTML = destText;
    edited.dispatchEvent(new Event('input', {
        bubbles: false
    }));

    input.innerHTML = sourceTexts;
    input.dispatchEvent(new Event('input', {
        bubbles: false
    }));

    edited.focus();
}

function resetAllTexts(sourceTexts, destText) {

    const input = document.getElementById("input");
    const edited = document.getElementById("edited");

    edited.innerHTML = "";
    edited.dispatchEvent(new Event('input', {
        bubbles: false
    }));

    input.innerHTML = "";
    input.dispatchEvent(new Event('input', {
        bubbles: false
    }));
}

function blockDestination() {
    const edited = document.getElementById("edited");
    edited.disabled = true;

    const copyBtn = document.getElementById("copy");
    copyBtn.disabled = true;

    const saveTableBtn = document.getElementById("save-as-table");
    saveTableBtn.disabled = true;
}

function unblockDestination() {
    const edited = document.getElementById("edited");
    edited.disabled = false;

    const copyBtn = document.getElementById("copy");
    copyBtn.disabled = false;

    const saveTableBtn = document.getElementById("save-as-table");
    saveTableBtn.disabled = false;
}