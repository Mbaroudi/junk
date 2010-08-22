"use strict";

var folder_list = '[{\
"id": "0",\
"parent_id": null,\
"name": "Current projects"\
},{\
"id": "1",\
"parent_id": null,\
"name": "Single actions"\
},{\
"id": "2",\
"parent_id": null,\
"name": "Programming"\
}]';

var project_list = '[{\
"id": "0",\
"parent_id": "0",\
"name": "Похозяйничать",\
"description": "Кухня и ванная",\
"starred": "1",\
"status": "active",\
"attachments": [],\
"type": "sequential"\
},{\
"id": "1",\
"parent_id": "1",\
"name": "Read",\
"description": "Books etc.",\
"starred": "0",\
"status": "on hold",\
"attachments": [],\
"type": "single actions"\
},{\
"id": "2",\
"parent_id": "2",\
"name": "Zoldatoff.ru",\
"description": "A site about me...",\
"starred": "0",\
"status": "completed",\
"attachments": [],\
"type": "parallel"\
}]';

var task_list = '[{\
"id": "0",\
"parent_id": "0",\
"name": "Купить герметик и водостойкий клей",\
"description": "3 герметика и 1 клей",\
"starred": "1",\
"status": "active",\
"attachments": [],\
"context_id": [0],\
"start": "01.01.2010",\
"due": "31.01.2010",\
"completed": "01.03.2010"\
},{\
"id": "1",\
"parent_id": "1",\
"name": "Прочитать документацию по Django",\
"description": "Oh! Django!",\
"starred": "0",\
"status": "skipped",\
"attachments": [],\
"context_id": [1],\
"start": "01.01.2010",\
"due": "31.01.2010",\
"completed": "01.03.2010"\
},{\
"id": "2",\
"parent_id": "2",\
"name": "Выбрать движок под zoldatoff.ru",\
"description": "A site about me...",\
"starred": "0",\
"status": "completed",\
"attachments": [],\
"context_id": [2],\
"start": "01.01.2010",\
"due": "31.01.2010",\
"completed": "01.03.2010"\
}]';

var context_list = '[{\
"id": "0",\
"name": "Moscow"\
},{\
"id": "1",\
"name": "iPad"\
},{\
"id": "2",\
"name": "Home"\
}]';

$.fn.gen_folderlist = function(flist) {
	var p_list = Array();
	var t = $(this).empty();
	$.each(flist, function(ind, val) {
		var el = $("<div>")
			.append("<span class=c_list_label>▾</span>")
			//.addClass("c_list_plus")
			.append("<input type='text' value='" + val.name + "' class='c_input_folder'/>")
			.append("<ul class='c_project_list'>");
		
		p_list = $.grep($.parseJSON(project_list), function(e, i) {
			return e.parent_id == val.id;
		});
			
		el.children("ul.c_project_list")
			//.hide()
			.gen_projectlist(p_list);
		
		el.children("span.c_list_label").toggle(function() {
				el.children("ul.c_project_list").show_projectlist();
			}, function() {
				el.children("ul.c_project_list").hide_projectlist();
		});
		
		t.append(el);
	});
	
	return t;
};

$.fn.gen_projectlist = function(plist) {
	var t = $(this).empty();
	$.each(plist, function(ind, val){
		var el = $("<li>")
			.append("<span class='c_star_button c_star_button_v'>★ &nbsp;</span>")
			.append("<input type='text' value='" + val.name + "' class='c_input_project'/>")
			.append("<input type='text' value='сегодня в 15:00'  class='c_input_date' />");
			
		var arr = [["Complete", "✓"], ["Delete", "✘"], ["Edit", "➜"], ["Attachment", "⌘"]]; 
		$.each(arr, function(i, v) {
			el.append("<span class='c_text_button' title= '" + v[0] + "'>" + v[1] + " &nbsp;</span>");
		});
		
		t.append(el);
	});
	
	//$(".c_text_button[title]").tooltip({ position: "bottom center" });
	return t;	
};

$.fn.hide_projectlist = function() {
	$(this).slideDown("fast");
	$(this).siblings("span.c_list_label").text("▾");
};

$.fn.show_projectlist = function() {
	$(this).slideUp("fast");
	$(this).siblings("span.c_list_label").text("▸");
};