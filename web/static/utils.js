
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

