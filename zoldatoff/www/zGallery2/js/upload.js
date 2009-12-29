/**
 * @author dsoldatov
 */
var dProgress, progress;
var currentObject, currentImage = null, //TODO
 currentAlbum = null, currentCategory = null;
var theImageList, theAlbumList, theCategoryList, theEditForm;

var mode = 'move';

/* Режим работы:
 * new
 * copy
 * move
 * edit
 */
$(document).ready(function(){
    theImageList = $('#imageThumbsUL');
    theAlbumList = $('#albumThumbsUL');
    theCategoryList = $('#categoryThumbsUL');
    theEditForm = $('#editForm');
    theFormImg = $('#formImg');
    
    // Disable right click
    $(document).bind("contextmenu", function(e){
        return false;
    });
    
    // Init progressbar
    $("#progressbar").progressbar({
        value: 0
    });
    
    // Init edit dialog
    theEditForm.dialog({
        autoOpen: false,
        modal: true,
        resizable: false,
        width: 320,
        open: function(){
            $('#title').focus();
        },
        buttons: {
            'OK': function(){
                var bValid = true;
                $('#title').removeClass('ui-state-error');
                $('#description').removeClass('ui-state-error');
                
                bValid = bValid && checkLength($('#title'));
                //bValid = bValid && checkLength($('#description'));
                
                if (mode != 'edit') {
                    myJson = $(this).data('json');
                    
                    switch ($(this).data('object')) {
                        case 'images':
                            myAction = 'updateimage';
                            myId = myJson.image_id;
                            break;
                        case 'albums':
                            myAction = 'updatealbum';
                            myId = myJson.album_id;
                            break;
                        case 'categories':
                            myAction = 'updatecategory';
                            myId = myJson.category_id;
                            break;
                    }
                    
                    if (bValid) {
                        $.getJSON(ajaxPath, {
                            action: myAction,
                            id: myId,
                            name: $('#title').val(),
                            description: $('#description').val()
                        }, function(jsonData){
                            $('#' + currentObject).data('json', jsonData.result).highlightMe();
                            unlockDisplay();
                        });
                        $(this).dialog('close');
                    }
                }
                
                if (mode == 'edit') {
                    switch ($(this).data('object')) {
                        case 'albums':
                            myAction = 'newalbum';
                            break;
                        case 'categories':
                            myAction = 'newcategory';
                            break;
                    }
                    
                    if (bValid) {
                        $.getJSON(ajaxPath, {
                            action: myAction,
                            name: $('#title').val(),
                            description: $('#description').val()
                        }, addNewElement);
                        $(this).dialog('close');
                    }
                }
                
                lockDisplay();
            },
            'Cancel': function(){
                $(this).dialog('close');
            }
        },
        close: function(){
            $('#title').removeClass('ui-state-error');
            $('#title').val('');
            $('#description').removeClass('ui-state-error');
            $('#description').val('');
            $('#validateTips').text("Plz, fill-in the information below");
        }
    });
    
    // Init modes menu
    $('.mode', '#modesDiv').click(function(){
        $('.mode', '#modesDiv').removeClass('activeMode');
        $(this).addClass('activeMode');
        
        switch ($(this).attr('id')) {
            case 'modeNew':
                mode = 'new';
                break;
            case 'modeCopy':
                mode = 'copy';
                break;
            case 'modeMove':
                mode = 'move';
                break;
            case 'modeEdit':
                mode = 'edit';
                break;
        }
        
        runMode();
        return false;
    });
    
    // Run Move mode
    $('#modeMove').click();
    
    // Init scroll interfaces
    $('#iUp').click(function(){
        theImageList.scrollThumbs(1);
        return false;
    });
    $('#iDown').click(function(){
        theImageList.scrollThumbs(-1);
        return false;
    });
    
    $('#aUp').click(function(){
        theAlbumList.scrollThumbs(1);
        return false;
    });
    $('#aDown').click(function(){
        theAlbumList.scrollThumbs(-1);
        return false;
    });
    
    $('#cUp').click(function(){
        theCategoryList.scrollThumbs(1);
        return false;
    });
    $('#cDown').click(function(){
        theCategoryList.scrollThumbs(-1);
        return false;
    });
    
    // Init remove interfaces
    $('#iRemove').click(function(){
        theImageList.removeElement();
        return false;
    });
    $('#aRemove').click(function(){
        theAlbumList.removeElement();
        return false;
    });
    $('#cRemove').click(function(){
        theCategoryList.removeElement();
        return false;
    });
    
    // Init add interfaces
    $('#modeNew').click(function(){
        mode = 'new';
        runMode();
        return false;
    });
    $('#aAdd').click(function(){
        theAlbumList.addElement();
        return false;
    });
    $('#cAdd').click(function(){
        theCategoryList.addElement();
        return false;
    });
});

function checkLength(element){
    if (element.val().length === 0) {
        element.addClass('ui-state-error');
        $('#validateTips').text("Field must not be empty!").effect("highlight", {}, 1500);
        return false;
    }
    else {
        return true;
    }
}

function addNewElement(jsonData){
    if (!catchError(jsonData)) {
        var N, myImg;
        if (jsonData.result.album_id) {
            N = theAlbumList.children().length + 1;
            
            myImg = $('<img/>').attr('id', 'alb' + N).attr('src', jsonData.result.image.thumb_src).attr('myID', jsonData.result.album_id).addClass('aThumbs').data('json', jsonData.result).make_droppable('icon');
            
            theAlbumList.append($('<li/>').append(myImg));
            
            growl("Album added", jsonData.result.name, jsonData.result.image.thumb_src);
        }
        
        if (jsonData.result.category_id) {
            N = theCategoryList.children().length + 1;
            
            myImg = $('<img/>').attr('id', 'cat' + N).attr('src', jsonData.result.image.thumb_src).attr('myID', jsonData.result.category_id).addClass('cThumbs').data('json', jsonData.result).make_droppable('icon');
            
            theCategoryList.append($('<li/>').append(myImg));
            
            growl("Category added", jsonData.result.name, jsonData.result.image.thumb_src);
        }
    }
    
    $.getJSON(ajaxPath, {
        object: 'categories'
    }, listCategories);
}

// Init mode and fetch data
function runMode(){
    lockDisplay();
    switch (mode) {
        case 'copy':
        case 'move':
            $('#iRemove').hide();
            $('#aRemove').hide();
            $('#cRemove').hide();
            $('#aAdd').hide();
            $('#cAdd').hide();
            $('#modeNew').hide();
            if (!currentCategory) {
                lockDisplay();
                $.getJSON(ajaxPath, {
                    object: 'categories'
                }, listCategories);
            }
            break;
        case 'edit':
            $('#iRemove').show(); //'pulsate', { times:2 }, 1000);
            $('#aRemove').show(); //'pulsate', { times:2 }, 1000);
            $('#cRemove').show(); //'pulsate', { times:2 }, 1000);
            $('#aAdd').show(); //'pulsate', { times:2 }, 1000);
            $('#cAdd').show(); //'pulsate', { times:2 }, 1000);
            $('#modeNew').show(); //'pulsate', { times:2 }, 1000);
            if (!currentCategory) {
                lockDisplay();
                $.getJSON(ajaxPath, {
                    object: 'categories'
                }, listCategories);
            }
            break;
        case 'new':
            $.getJSON(ajaxPath, {
                object: 'newimages'
            }, listNewImages);
            break;
    }
    
    if (mode != 'new') {
        $.getJSON(ajaxPath, {
            object: 'categories'
        }, listCategories);
        if (currentAlbum) {
            lockDisplay();
            $.getJSON(ajaxPath, {
                object: 'images',
                album_id: currentAlbum
            }, listImages);
        }
        if (currentCategory) {
            lockDisplay();
            $.getJSON(ajaxPath, {
                object: 'albums',
                category_id: currentCategory
            }, listAlbums);
        }
    }
}

// Вывести список загруженных в папку upload изображений
function listNewImages(jsonData){
    progress = dProgress = 0;
    list(jsonData, 'newimages');
}

//Вывести список изображений из альбома
function listImages(jsonData){
    list(jsonData, 'images');
}

//Вывести список альбомов из категории
function listAlbums(jsonData){
    list(jsonData, 'albums');
}

//Вывести список категорий
function listCategories(jsonData){
    list(jsonData, 'categories');
}

//Вывод списка объектов типа object
function list(jsonData, object){
    if (catchError(jsonData)) {
        return false;
    }
    
    var nObjects;
    
    // Очищаем соответствующий список
    switch (object) {
        case 'newimages':
            nObjects = jsonData.objectlist.length;
            theImageList.empty();
            theAlbumList.empty();
            theCategoryList.empty();
            break;
        case 'images':
            if (jsonData.objectlist.image_list) {
                nObjects = jsonData.objectlist.image_list.length;
            }
            else {
                nObjects = 0;
            }
            theImageList.empty();
            $('#iCaption').html('Images from album "' + jsonData.objectlist.name + '"');
            break;
        case 'albums':
            if (jsonData.objectlist.album_list) {
                nObjects = jsonData.objectlist.album_list.length;
            }
            else {
                nObjects = 0;
            }
            theAlbumList.empty();
            $('#aCaption').html('Albums from category "' + jsonData.objectlist.name + '"');
            break;
        case 'categories':
            nObjects = jsonData.objectlist.category_list.length;
            theCategoryList.empty();
            break;
    }
    
    //Заполняем соответствующий список
    for (var i = 0; i < nObjects; i++) {
        switch (object) {
            case 'newimages':
                theImageList.append('<li><img id="img' + i + '" class="iThumbs" src="css/loader.gif"/> </li>');
                break;
            case 'images':
                theImageList.append('<li><img id="img' + i + '" class="iThumbs" src="' + jsonData.objectlist.image_list[i].thumb_src + '"/> </li>');
                $('#img' + i).attr('myID', jsonData.objectlist.image_list[i].image_id).data('json', jsonData.objectlist.image_list[i]);
                if (jsonData.objectlist.image_list[i].image_id == currentImage) {
                    $('#img' + i).parent().addClass('active');
                }
                break;
            case 'albums':
                theAlbumList.append('<li><img id="alb' + i + '" class="aThumbs" src="' + jsonData.objectlist.album_list[i].image.thumb_src + '"/> </li>');
                $('#alb' + i).attr('myID', jsonData.objectlist.album_list[i].album_id).data('json', jsonData.objectlist.album_list[i]);
                if (jsonData.objectlist.album_list[i].album_id == currentAlbum) {
                    $('#alb' + i).parent().addClass('active');
                //$.getJSON(ajaxPath, {object: 'images',album_id: currentAlbum}, listImages);
                }
                break;
            case 'categories':
                theCategoryList.append('<li><img id="cat' + i + '" class="cThumbs" src="' + jsonData.objectlist.category_list[i].image.thumb_src + '"/> </li>');
                $('#cat' + i).attr('myID', jsonData.objectlist.category_list[i].category_id).data('json', jsonData.objectlist.category_list[i]);
                if (jsonData.objectlist.category_list[i].category_id == currentCategory) {
                    $('#cat' + i).parent().addClass('active');
                //$.getJSON(ajaxPath, {object: 'albums', category_id: currentCategory}, listAlbums);
                }
                break;
        }
    }
    
    //Позиционируем изображения
    $('li img').load(function(){
        $(this).center();
    });
    
    
    /* Здесь нужно применять разную логику для разных режимов работы:
     * copy images/albums
     * move images/albums
     * create/edit albums/categories/images
     */
    switch (object) {
        case 'newimages':
            // Выводим поверх всего DIV с probressbar-ом
            dProgress = 100 / nObjects;
            $('#topDiv').show();
            $("#progressbar").progressbar('option', 'value', 0);
            
            // Для каждого файла запускаем процедуру импорта в галерею
            for (var i = 0; i < nObjects; i++) {
                $.getJSON(ajaxPath, {
                    filename: jsonData.objectlist[i].filename,
                    number: i
                }, getUploadStatus);
            }
            
            break;
            
        case 'images':
            // Изображения можно выделять
            $('.iThumbs').click(function(){
                if (mode == 'edit') {
                    $('.iThumbs').parent().removeClass('active');
                }
                $(this).parent().toggleClass('active');
                if ($(this).parent().hasClass('active')) {
                    currentImage = $(this).attr('myID');
                }
                return false;
            });
            
            $('.iThumbs').dblclick(function(){
                if (mode != 'edit') {
                    $(this).editMe(object, $(this).data('json'));
                }
                return false;
            });
            
            // Изображения можно перетаскивать внутри группы images2albums / images2all
            if (mode == 'edit') {
                $('.iThumbs').make_draggable('icon');
            }
            else {
                $('.iThumbs').make_draggable('images2albums');
            }
            
            break;
            
        case 'albums':
            // При выделении альбома подгружаются изображения из него
            $('.aThumbs').click(function(){
                lockDisplay();
                $('.aThumbs').parent().removeClass('active');
                $(this).parent().addClass('active');
                $.getJSON(ajaxPath, {
                    object: 'images',
                    album_id: $(this).attr('myID')
                }, listImages);
                currentImage = null;
                currentAlbum = $(this).attr('myID');
                if (mode != 'edit') {
                    $(".aThumbs").droppable('enable');
                    $(this).droppable('disable');
                }
                return false;
            });
            
            $('.aThumbs').dblclick(function(){
                if (mode != 'edit') {
                    $(this).editMe(object, $(this).data('json'));
                }
                return false;
            });
            
            // На альбомы можно перетаскивать изображения
            if (mode == 'edit') {
                $(".aThumbs").make_droppable('icon');
            }
            else {
                $(".aThumbs").make_droppable('images2albums');
            }
            
            // Альбомы можно перетаскивать внутри группы albums2categories
            $('.aThumbs').make_draggable('albums2categories');
            
            break;
            
        case 'categories':
            // При выделении категории подгружаются ее альбомы
            $('.cThumbs').click(function(){
                lockDisplay();
                $('.cThumbs').parent().removeClass('active');
                $(this).parent().addClass('active');
                $.getJSON(ajaxPath, {
                    object: 'albums',
                    category_id: $(this).attr('myID')
                }, listAlbums);
                currentAlbum = null;
                currentCategory = $(this).attr('myID');
                if (mode != 'edit') {
                    $(".cThumbs").droppable('enable');
                    $(this).droppable('disable');
                }
                return false;
            });
            
            $('.cThumbs').dblclick(function(){
                if (mode != 'edit') {
                    $(this).editMe(object, $(this).data('json'));
                }
                return false;
            });
            
            // На категории можно перетаскивать альбомы
            if (mode == 'edit') {
                $(".cThumbs").make_droppable('icon');
            }
            else {
                $(".cThumbs").make_droppable('albums2categories');
            }
            
            break;
    }
    
    unlockDisplay();
    return true;
}

function findMe(jsonData, removeMe){
    if (catchError(jsonData)) {
        return null;
    }
    
    var myClass, myID, myMessage;
    myMessage = new Array();
    
    if (jsonData.result.image_id) {
        myID = jsonData.result.image_id
        myClass = '.iThumbs';
        myMessage.object = 'Image';
        myMessage.thumb = jsonData.result.thumb_src;
    }
    else 
        if (jsonData.result.album_id) {
            myID = jsonData.result.album_id
            myClass = '.aThumbs';
            myMessage.object = 'Album';
            myMessage.thumb = jsonData.result.image.thumb_src;
        }
        else {
            if (jsonData.result.category_id) {
                myID = jsonData.result.category_id
                myClass = '.cThumbs';
                myMessage.object = 'Category';
                myMessage.thumb = jsonData.result.image.thumb_src;
            }
        }
    
    $(myClass).each(function(){
        var t = $(this);
        if (t.attr('myID') == myID) {
            t.highlightMe();
            if (mode == 'move' || removeMe) {
                t.parent().hide('explode');
            }
        }
    });
    
    unlockDisplay();
    return myMessage;
}

function getRemoveStatus(jsonData){
    var f = findMe(jsonData, true);
    if (f) {
        growl(f.object + ' successfully removed', jsonData.result.name, f.thumb);
        switch (f.object) {
            case 'Category':
                theAlbumList.empty();
                theImageList.empty();
                break;
            case 'Album':
                theImageList.empty();
                break;
        }
    }
}

// Убираем изображение перемещенного файла и сообщаем об этом
function displayDropStatus(jsonData){
    var f = findMe(jsonData);
    if (f) {
        if (mode == 'move') {
            growl(f.object + ' successfully moved', jsonData.result.name, f.thumb);
        }
        if (mode == 'copy') {
            growl(f.object + ' successfully copied', jsonData.result.name, f.thumb);
        }
    }
}

// Выводим изображение обработанного файла и сообщаем об этом
function getUploadStatus(jsonData){
    if (!catchError(jsonData)) {
        $('#img' + jsonData.result.number).attr('src', jsonData.result.filename);
        growl('Image imported in gallery', jsonData.result.filename, jsonData.result.filename);
    }
    
    progress += dProgress;
    
    $("#progressbar").progressbar('option', 'value', progress);
    if (progress > 99) {
        $('#topDiv').hide();
        $('#modeMove').click();
    }
}

function displayThumbAction(jsonData){
    if (!catchError(jsonData)) {
        $('#' + currentObject).attr('src', jsonData.result.image.thumb_src).data('json', jsonData.result).highlightMe();
        growl('Album/category icon successfully changed:', jsonData.result.name, jsonData.result.image.thumb_src);
    }
}

function catchError(jsonData){
    unlockDisplay();
    if (jsonData.result && jsonData.result.error) {
        growl('Error!', jsonData.result.error, null);
        return true;
    }
    return false;
}

function lockDisplay(){
    return $('#lockDiv').show();
}

function unlockDisplay(){
    return $('#lockDiv').hide();
}
