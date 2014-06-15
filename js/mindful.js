(function() {
    var BLACK_LIST = [];
    var WOULD_RATHER = [];

    var match = false;
    var href = window.location.href;
    var site_name = null;
    var rather = null;
    chrome.storage.sync.get(null, function(settings) {
      BLACK_LIST = settings.websites;
      WOULD_RATHER = settings.thingsToDo;
      init();
      initialized = true;

    });
    function init() {
        for (var i in BLACK_LIST) {
            if (href.indexOf(BLACK_LIST[i].url) != -1) {
                match = true;
                site_name = BLACK_LIST[i].url;
                rather = WOULD_RATHER[Math.floor(Math.random() * WOULD_RATHER.length)].title;
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
            "</div>",
            "<a href='http://chrisgin.com' id='mindfulBrowsingPhotoCredit' target='_blank'>Photo by Chris Gin</a>"
            ].join("");
            ele.style.height = height + "px";
            document.body.appendChild(ele);
        }
    }
})();
