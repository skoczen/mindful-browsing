(function() {
    var BLACK_LIST = ["facebook", "news.google.com", "test.html" ];
    var WOULD_RATHER = ["meditate for a minute", "go for a walk", "take ten deep breaths", "read an article on beacon"]
//     var IMAGES = [
// 01510_sunsetbeach_2560x1600-1.jpg
// 01510_sunsetbeach_2560x1600.jpg
// 01643_goodmorning_2560x1600.jpg
// 01689_beautifulmorning_2560x1600.jpg
// 01725_thelookout_2560x1600.jpg
// 01806_hunuafalls_2560x1600.jpg
// 01991_autumnlake_2560x1600.jpg
// 02003_darknessrising_2560x1600.jpg
// 02056_morninglight_1920x1200.jpg
//     ]

    var match = false;
    var href = window.location.href;
    var site_name = null;
    var rather = null;

    for (var i in BLACK_LIST) {
        if (href.indexOf(BLACK_LIST[i]) != -1) {
            match = true;
            site_name = BLACK_LIST[i];
            rather = WOULD_RATHER[Math.floor(Math.random() * WOULD_RATHER.length)];
            break;
        }
    }
    if (match) {
        var body = document.body;
        var html = document.documentElement;

        var height = Math.max( body.scrollHeight, body.offsetHeight,
            html.clientHeight, html.scrollHeight, html.offsetHeight );
        var ele =  document.createElement("div");
        ele.id="mindfulBrowsingConfirm";
        ele.innerHTML = [
        "<div class='mindfulBrowsingHeading'>",
            "<h1>Are you sure you want to go to "+site_name+"?</h1>",
            "<h2>You said you'd usually rather "+rather+". :)</h2>",
        "</div>",
        "<div class='options'>",
            "<a class='mindfulBtn' href='javascript:var ele = document.getElementById(\"mindfulBrowsingConfirm\");ele.parentNode.removeChild(ele);'>Yes, for 5 minutes</a>",
            "<a class='mindfulBtn' href='javascript:window.close();'>Actually, nah.</a>",
        "</div>"
        ].join("");
        ele.style.height = height + "px";
        document.body.appendChild(ele);
    }
})();
