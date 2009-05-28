/**
 * @author dsoldatov
 */

// Универсальная функция инициализации txt/xml запроса
 function createRequest() {
 	var request = null;
	
	try {
		request = new XMLHttpRequest();
	} catch(trymicrosoft) {
		try {
			request = new ActiveXObject("Msxml2.XMLHTTP");
		} catch (othermicrosoft) {
			try {
				request = new ActiveXObject("Microsoft.XMLHTTP");
			} catch (failed) {
				request = null;
			}
		}
	}
	
	if (request == null)
		alert("Error using AJAX");
	else
		return request;
 }
 
 // Универсальная функция отсылки txt/xml запроса
 function sendRequest(request, url, callback) {
 	request.onreadystatechange = callback;
	request.open("GET", url, true);
	request.send(null);
 }
 
 // Создаем таблицу со списком закачиваемых файлов
 function createTable() {
 	// Читаем JSON с сервера
 	var jsonData = null;
	
 	if (reqFiles.readyState == 4) {
		if (reqFiles.status == 200) {
			jsonData = eval('(' + reqFiles.responseText + ')');
			reqFiles = null;
			
			if (jsonData) {
				nFiles = jsonData.filelist.length-1;
				
				// заполняем таблицу
				var myHTML = "<tr><th>Image</th><th>Original</th><th>Full</th><th>Normal</th><th>Small</th><th>Deleted</th><th>MySQL</th><th>All</th></tr>";
				for (var i=0; i<jsonData.filelist.length-1; i++){
					myHTML += '<tr>';
					myHTML += '<td><img id="img' + i + '" src="icons/loader_2_fff.gif" style="max-height:30px" /></td>';
					myHTML += '<td>' + jsonData.filelist[i].filename + '</td>';
					myHTML += '<td id="full' + i + '"><img src="icons/loader_2_fff.gif" /></td>';
					myHTML += '<td id="norm' + i + '"><img src="icons/loader_2_fff.gif" /></td>';
					myHTML += '<td id="small' + i + '"><img src="icons/loader_2_fff.gif" /></td>';
					myHTML += '<td id="del' + i + '"><img src="icons/loader_2_fff.gif" /></td>';
					myHTML += '<td id="sql' + i + '"><img src="icons/loader_2_fff.gif" /></td>';
					myHTML += '<td><img id="yesno' + i + '" src="icons/loader_2_fff.gif" /></td>';
					myHTML += '</tr>';
				}
				document.getElementById("mainT").innerHTML = myHTML;
					
				// Создаем массивы запросов		
				for (var i = 0; i < jsonData.filelist.length - 1; i++) {
					reqFull[i] = createRequest();		
					reqNorm[i] = createRequest();			
					reqSmall[i] = createRequest();
					reqDel[i] = createRequest();
					reqSQL[i] = createRequest();
					
					myImages[i] = new Array();
					myImages[i]["full"] = myImages[i]["norm"] = myImages[i]["small"] = 0;
					myImages[i]["del"] = myImages[i]["sql"] = 0;
					myImages[i]["filename"] = jsonData.filelist[i].filename;
				}
				
				// Отсылаем запросы на генерацию изображений
				for (var i = 0; i < jsonData.filelist.length - 1; i++) {
					var url = "upload.php?filename=" + escape(jsonData.filelist[i].filename) + "&filesize=";
					sendRequest(reqFull[i],  url + "full",   getStatus);
					sendRequest(reqNorm[i],  url + "normal", getStatus);
					sendRequest(reqSmall[i], url + "small",  getStatus);
				}
			}
		} else 
			alert("Request status is " + reqFiles.status);
	}
 }
 
 // Проверка состояния выполнения запросов
 function getStatusTmp(request, size, i) {
 	// Читаем JSON с сервера
 	var jsonData = null;
	
	if (request.readyState == 4) {
		if (request.status == 200) {
			jsonData = eval('(' + request.responseText + ')');
			request = null;
			
			if (jsonData) {
				// Проверяем, успешно ли завершилась операция на сервере
				if (jsonData.result[0].error == "OK") {
					// запоминаем, что заполнили ячейку
					myImages[i][size] = 1;
					//...вот этим вот значением 
					myImages[i][size + "name"] = jsonData.result[0].data;
					
					// выводим картинку в первом столбце
					if (size == "small") 
						document.getElementById("img" + i).src = jsonData.result[0].data;
				}
				else // иконка в последней колонке
					document.getElementById("yesno" + i).src = "icons/no.gif";

				// Обновляем значение ячейки
				document.getElementById(size + i).innerHTML = jsonData.result[0].data;
				
				// Проверяем, сгенерировались ли изображения
				// Проверяем, прошли ли все операции
				var testLoad = myImages[i]["full"] + myImages[i]["norm"] + myImages[i]["small"];
				if (myImages[i]["del"] == 1) testLoad ++;
				if (myImages[i]["sql"] == 1) testLoad ++;
				switch (testLoad) {
					case 3:
						// Удаляем первоначальное изображение
						var url = "upload.php?filename=" + escape(myImages[i]["filename"]) + "&filesize=delete";
						sendRequest(reqDel[i], url, getStatus);
						
						// Добавляем данные об изображении в БД
						url = "upload.php?fullname=" + escape(myImages[i]["fullname"]);
						url += "&normname=" + escape(myImages[i]["normname"]);
						url += "&smallname=" + escape(myImages[i]["smallname"]);
						url += "&uploaddate=" + escape(uploaddate);
						sendRequest(reqSQL[i], url + "full", getStatus);
						break;
					case 5:
						// иконка в последней колонке
						document.getElementById("yesno" + i).src = "icons/yes.gif";
						break;
				}
			}
		}
		else // Если ответ сервера не 200 (OK), выводим номер статуса
			document.getElementById(size + i).innerHTML = request.status;
	}		
 }
 
 // Запуск проверок состояния запросов
 function getStatus() {
 	for (var i = 0; i < nFiles; i++) {
		if (myImages[i]["full"]==0) getStatusTmp(reqFull[i], "full", i);
		if (myImages[i]["norm"]==0) getStatusTmp(reqNorm[i], "norm", i);
		if (myImages[i]["small"]==0) getStatusTmp(reqSmall[i], "small", i);
		if (myImages[i]["full"] + myImages[i]["norm"] + myImages[i]["small"] == 3 && myImages[i]["del"]==0) getStatusTmp(reqDel[i], "del", i);
		if (myImages[i]["full"] + myImages[i]["norm"] + myImages[i]["small"] == 3 && myImages[i]["sql"]==0) getStatusTmp(reqSQL[i], "sql", i);
	}
 }
