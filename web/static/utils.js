
function showProgress(percent){
    percent = percent>100?100: percent;
    var scrollPercent = percent + "%";
    var element = document.getElementById("progress");
    element.style.setProperty("--fill", scrollPercent);
    element.style.setProperty("display", 'block');

    var span = element.getElementsByTagName("span")[0];
    //span.style.setProperty("right", percent/2+"%");
    span.innerHTML = percent + "%";
}

function hideProgress(){
    var element = document.getElementById("progress");
    element.style.setProperty("--fill", 0);
    element.style.setProperty("display", 'none');
    var span = element.getElementsByTagName("span")[0];
    //span.style.setProperty("right", null);
    span.innerHTML = null;
}

function blockInput(){

    var fromFileBtn = document.getElementById("fileload-btn");
    fromFileBtn.disabled = true;

    var sendFromTextBtn = document.getElementById("send-text-for-translation");
    sendFromTextBtn.disabled = true;

    var input = document.getElementById("input");
    input.setAttribute("contenteditable", false);

}

function unblockInput(){

    var fromFileBtn = document.getElementById("fileload-btn");
    fromFileBtn.disabled = false;

    var sendFromTextBtn = document.getElementById("send-text-for-translation");
    sendFromTextBtn.disabled = false;

    var input = document.getElementById("input");
    input.setAttribute("contenteditable", true);

}

function setCPU(percent){

    var color = '#9ACD32';
    if(percent>70){
        color = 'red';
    } else if(percent>30){
        color = 'gold';
    }

    var cpu = document.getElementById("cpu");
    cpu.style.setProperty("display", 'block');
    cpu.style.borderColor =color;

    var cpuSpan = document.getElementById("cpu-span");
    cpuSpan.innerHTML = percent + '%';
    cpu.style.setProperty("color", color);
}


