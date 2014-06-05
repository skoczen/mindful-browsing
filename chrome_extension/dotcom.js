console.log(window.location.href)
// window.onload = function() {
    // alert(window.location.href);
    // window.pauseConfirm = {};
    // alert(window.pauseConfirm)

    if (window.location.href.indexOf("facebook") != -1) {
        var body = document.body,
        html = document.documentElement;

        var height = Math.max( body.scrollHeight, body.offsetHeight,
            html.clientHeight, html.scrollHeight, html.offsetHeight );
        var ele =  document.createElement("div");
        ele.id="pause_confirm";
        ele.innerHTML = [
        "<h1>Are you sure you want to go to facebook?</h1>",
        "<div class='options'>",
            "<a href='javascript:var ele = document.getElementById(\"pause_confirm\");ele.parentNode.removeChild(ele);'>Yes</a>",
            "<a href='#'>No, thanks.</a>",
        "</div>"
        ].join("");
        ele.style.height = height;
        document.body.appendChild(ele);
    }

// };
