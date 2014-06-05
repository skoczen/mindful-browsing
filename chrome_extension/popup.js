chrome.webNavigation.onCommitted.addListener(function(e) {
    if (".com" in e.url) {
        document.getElementById("foo").innerHTML = "goog!";
    }
});