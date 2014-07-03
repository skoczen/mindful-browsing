(function(){
    window.mindfulBrowsing = {};
    var settings = {};
    var BLANK_WEBSITE = { "url": ""};
    var BLANK_THING = { "title": ""};
    var websites = [
        { "url": "facebook.com" },
        { "url": "twitter.com" },
        { "url": ""}
    ];
    var thingsToDo = [
        { "title": "take five deep breaths" },
        { "title": "take a quick walk" },
        { "title": ""}
    ];
    var timeouts = {};
    var currentPhoto;

    var initialized = false;

    var saveSettings = function() {
        // Save it using the Chrome extension storage API.
        if (initialized === true) {
            var saveWebsites = [];
            for (var w in websites) {
                if (websites[w].url !== "") {
                    saveWebsites.push(websites[w]);
                }
            }
            var saveThingsToDo = [];
            for (var t in thingsToDo) {
                if (thingsToDo[t].title !== "") {
                    saveThingsToDo.push(thingsToDo[t]);
                }
            }
            chrome.storage.sync.set({
                "websites": saveWebsites,
                "thingsToDo": saveThingsToDo,
                "timeouts": timeouts,
                "currentPhoto": currentPhoto
            }, function() {
              // Notify that we saved.
            });
        }
    };
    var loadSettings = function() {
        // Save it using the Chrome extension storage API.
        chrome.storage.sync.get(null, function(settings) {
          // Notify that we saved.
          if (settings.websites) {
            websites = settings.websites;  
          }
          if (settings.thingsToDo) {
            thingsToDo = settings.thingsToDo;
          }
          if (settings.timeouts) {
            timeouts = settings.timeouts;
          }
          currentPhoto = settings.currentPhoto;

          init();
          initialized = true;
        });
    };
    var init = function() {
        var ractive = new Ractive({
            // The `el` option can be a node, an ID, or a CSS selector.
            el: 'container',
            template:
            '<h2>I want to be mindful of spending my time on:</h2>'+
            '  <div class="responses">'+
            '      {{#websites:num}}'+
            '      <div class="response"><label>http://</label><input type="text" value="{{url}}" /><a class="removeX" on-click="removeSite">&#x2716;</a></div>'+
            '      {{/websites}}'+
            '      <div class="response"><label></label><a on-click="addSite" class="mindfulBtn">Add another</a></div>'+
            '  </div>'+
            '  <h2>Usually, I\'d rather:</h2>'+
            '  <div class="responses thingsToDo">'+
            '      {{#thingsToDo:num}}'+
            '      <div class="response"><input type="text" placeholder="something small and specific" value="{{title}}" /><a class="removeX" on-click="removeThing">&#x2716;</a></div>'+
            '      {{/thingsToDo}}'+
            '      <div class="response"><a on-click="addThing" class="mindfulBtn">Add another</a></div>'+
            '  </div>'+
            '',
            data: {
            name: 'world',
            websites: websites,
            thingsToDo: thingsToDo
            }
        });
        ractive.on({
            addSite: function() {
                websites.push(BLANK_WEBSITE);
                return false;
            },
            addThing: function() {
                thingsToDo.push(BLANK_THING);
                return false;
            },
            removeSite: function(event) {
                websites.splice(event.index.num, 1);
                return false;
            },
            removeThing: function(event) {
                thingsToDo.splice(event.index.num, 1);
                return false;
            }
        });
        ractive.observe('websites', function ( newValue, oldValue, keypath ) {
            websites = newValue;
            saveSettings();
        }, false);
        ractive.observe('thingsToDo', function ( newValue, oldValue, keypath ) {
            thingsToDo = newValue;
            saveSettings();
        }, false);
    }
    loadSettings();
})();