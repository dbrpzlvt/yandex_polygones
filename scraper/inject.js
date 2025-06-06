// Inject custom script on yandex.ru/maps load
const nullthrows = (v) => {
    if (v == null) throw new Error("it's a null");
    return v;
}

function injectCode(src) {
    const script = document.createElement('script');
    // This is why it works!
    script.src = src;
    script.onload = function() {
        this.remove();
    };

    // This script runs before the <head> element is created,
    // so we add the script to <html> instead.
    nullthrows(document.head || document.documentElement).appendChild(script);
}

// Вставляем custom.js как внешний скрипт
injectCode('custom.js');
//injectCode(chrome.runtime.getURL('/scripts/custom.js'));
var port = chrome.runtime.connect({name: "knockknock"});

const data = []

// When new data obtained (injected code > content script)
window.addEventListener("FromPage", function(evt) {
	var detail = evt.detail
    if (data.find(x => x.name === detail.name))
        return console.log("Объект " + detail.name + " уже занесен")
    data.push({ name: detail.name, polygons: detail.polygons })
    // chrome.storage.local.set({ 'gatheredPolygons': data })
}, false);
