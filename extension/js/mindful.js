(function() {
    var websites = [];
    var thingsToDo = [];

    var match = false;
    var href = window.location.href;
    var site_name = null;
    var rather = null;
    var was_in_timeout = false;
    var timeouts;
    var currentPhoto;

    // Storage:
    // {
    //     "websites": ["foo.com", "bar.com"],
    //     "thingsToDo": ["go for a walk", "etc"],
    //     "timeouts": {
    //         "foo.com": 1234532341231  // ms since epoch when timeout expires
    //     },
    //     "currentPhoto": {
    //         "next_update": 12312431242,
    //         "credit": "Chris Gin",
    //         "credit_url": "http://chrisgin.com",
    //         "start_date": 1404448425891,
    //         "start_date_human": "June 26 2014",
    //         "url": "https://mindfulbrowsing.org/photos/2.jpg"
    //     }
    // }

    chrome.storage.sync.get(null, function(settings) {
      websites = settings.websites || {};
      thingsToDo = settings.thingsToDo || {};
      timeouts = settings.timeouts || {};
      currentPhoto = settings.currentPhoto || {};
      initialized = true;
      init();
    });
    var mindfulBrowsing = window.mindfulBrowsing || {};
    mindfulBrowsing.confirmClicked = function() {
        var ele = document.getElementById("mindfulBrowsingConfirm");
        ele.parentNode.removeChild(ele);
        var now = new Date();
        // Set for 10 minutes from now.
        var timeout_diff = (10*60000);
        timeouts[site_name] = now.getTime() + timeout_diff;
        mindfulBrowsing.saveSettings();
        was_in_timeout = true;
        setTimeout(mindfulBrowsing.addOverlay, timeout_diff);
        return false;
    };
    mindfulBrowsing.saveSettings = function() {
        // Save it using the Chrome extension storage API.
        if (initialized === true) {
            var saveWebsites = [];
            for (var w in websites) {
                if (websites[w].url != "") {
                    saveWebsites.push(websites[w]);
                }
            }
            var saveThingsToDo = [];
            for (var t in thingsToDo) {
                if (thingsToDo[t].url != "") {
                    saveThingsToDo.push(thingsToDo[t]);
                }
            }
            chrome.storage.sync.set({
                "websites": saveWebsites,
                "thingsToDo": saveThingsToDo,
                "timeouts": timeouts,
                "currentPhoto": currentPhoto,
            }, function() {
              // Notify that we saved.
            });
        }
    };
    mindfulBrowsing.addOverlay = function() {
        rather = thingsToDo[Math.floor(Math.random() * thingsToDo.length)].title;
        var body = document.body;
        var html = document.documentElement;

        var height = Math.max( body.scrollHeight, body.offsetHeight,
            html.clientHeight, html.scrollHeight, html.offsetHeight );
        var go_verb = (was_in_timeout)? "stay on" : "spend time on";

        var ele = document.createElement("div");
        ele.id="mindfulBrowsingConfirm";
        ele.innerHTML = [
        "<div class='mindfulBrowsingHeading'>",
            "<h1>Are you sure you want to " + go_verb + " " +site_name+"?</h1>",
            "<h2>You said you'd usually rather "+rather+". :)</h2>",
        "</div>",
        "<div class='options'>",
            "<a class='mindfulBtn' id='mindfulBrowsingContinue' href='#'>Yes, for 10 minutes.</a>",
            "<a class='mindfulBtn' id='mindfulBrowsingLeave' href='javascript:window.close()'>Actually, nah.</a>",
        "</div>",
        "<a href='" + currentPhoto["credit_url"] + "' id='mindfulBrowsingPhotoCredit' target='_blank'>Photo by " + currentPhoto["credit"] + "</a>"
        ].join("");
        ele.style.height = height + "px";
        ele.style.background = "url('" + currentPhoto["url"] + "') no-repeat center center fixed";
        ele.style.backgroundSize = "cover";
        document.body.appendChild(ele);
        
        btn = document.getElementById("mindfulBrowsingContinue");
        btn.onclick = mindfulBrowsing.confirmClicked;
    };
    window.mindfulBrowsing = mindfulBrowsing;
    function init() {
        var now = new Date();
        if (currentPhoto["next_update"] === undefined || currentPhoto["next_update"] < now.getTime()) {
            var photo_index = 0;
            for (photo_index=0; photo_index<window.mindfulBrowsing.photoInfo.photos.length; photo_index++) {
                if (window.mindfulBrowsing.photoInfo.photos[photo_index]["start_date"] > now.getTime()) {
                    break;
                }
            }
            photo_index = (photo_index > 0) ? photo_index: 1;
            currentPhoto = window.mindfulBrowsing.photoInfo.photos[photo_index-1];
            currentPhoto["next_update"] = now.getTime() + (1000*60*60*24);
            mindfulBrowsing.saveSettings();
        }
        for (var i in websites) {
            if (href.indexOf(websites[i].url) != -1) {
                site_name = websites[i].url;

                match = true;
                // Check timeouts
                if (site_name in timeouts) {
                    if (timeouts[site_name] < now.getTime()) {
                        delete timeouts[site_name];
                    } else {
                        match = false;
                        was_in_timeout = true;
                        setTimeout(mindfulBrowsing.addOverlay, timeouts[site_name] - now.getTime());
                    }
                }
                if (match) {
                    
                    break;
                }
            }
        }
        if (match) {
            mindfulBrowsing.addOverlay();
        }
    }
})();
