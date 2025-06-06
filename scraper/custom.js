// Вставка своего скрипта в модуль Fetch
var oldFetch = fetch;  // must be on the global scope
fetch = async function(url, options) {
    var response = await oldFetch(url, options)
	// Detect completed request that we need
    // Проверка статуса ответа
    if (!response.ok) {
        console.log("Отправляем запрос: ", url);
        console.log("Ответ от сервера: ", response);
        console.error("Ошибка при получении данных:", response.status);
        return response;
    }
    // Перехват нужного запроса
    if (url.match(/\/maps\/api\/search\?[^ ]*ajax=(.*)/)) {
        handleBody(response.body)
    } else {
        console.log("Отправляем запрос: ", url);
        console.log("Ответ от сервера: ", response);
        console.error("Ошибка при получении данных:", response.status);
    }
    return response
}

// Расшифровка ReadableStream
function handleBody(stream) {
	var reader = stream.getReader();
	var result = ""
	var pump = reader =>
	  reader.read().then(({done, value}) => {
		result += new TextDecoder("utf-8").decode(value)
		if (!done) {
		  // Subsequent read() when it's not done yet
		  return pump(reader);
		} else {
			passData(result)
		}
	  });

	// Initial read()
	pump(reader)
}

// Добыча информации
function passData(string) {
	var json = JSON.parse(string)
	try {
		const result = json.data.exactResult
		const array = result.displayGeometry.geometries
		const title = result.title
        const addr = result.address
        const full_address = result.description
		
		var polygons = []
		for(var poly of array) polygons.push(poly.coordinates[0])
		
		var object = { name: title, address: addr, description: full_address, polygons }
		
		var event = new CustomEvent("FromPage", { detail: object });
		window.dispatchEvent(event); // saves to local storage to show in popup
		
		var clipboard = JSON.stringify(object, null, 2)
		copy(clipboard, "text/plain") // copies to clipboard
	} catch (err) { console.log(err) }
}

// Загрузка в буфер обмена (ctrl c)
function copy(str, mimeType) {
  document.oncopy = function(event) {
    event.clipboardData.setData(mimeType, str);
    event.preventDefault();
  };
  document.execCommand("copy", false, null);
}