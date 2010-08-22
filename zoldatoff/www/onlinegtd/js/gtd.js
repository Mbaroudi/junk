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
"start_date": "01.01.2010",\
"due_date": "31.01.2010",\
"complete_date": "01.03.2010",\
"attachments": [],\
"type": "sequential"\
},{\
"id": "1",\
"parent_id": "1",\
"name": "Read",\
"description": "Books etc.",\
"starred": "0",\
"status": "on hold",\
"start_date": "01.01.2010",\
"due_date": "31.01.2010",\
"complete_date": "01.03.2010",\
"attachments": [],\
"type": "single actions"\
},{\
"id": "2",\
"parent_id": "2",\
"name": "Zoldatoff.ru",\
"description": "A site about me...",\
"starred": "0",\
"status": "completed",\
"start_date": "01.01.2010",\
"due_date": "31.01.2010",\
"complete_date": "01.03.2010",\
"attachments": [],\
"type": "parallel"\
},{\
"id": "3",\
"parent_id": "2",\
"name": "onlinegtd.ru",\
"description": "GTD",\
"starred": "1",\
"status": "skipped",\
"start_date": "01.01.2010",\
"due_date": "31.01.2010",\
"complete_date": "01.03.2010",\
"attachments": [],\
"type": "parallel"\
}]';

var task_list = '[{\
"id": "0",\
"parent_id": "0",\
"name": "Купить герметик и водостойкий клей",\
"description": "3 герметика и 1 клей",\
"starred": "0",\
"status": "active",\
"attachments": [],\
"context_id": [0],\
"start_date": "01.01.2010",\
"due_date": "31.01.2010",\
"complete_date": "01.03.2010"\
},{\
"id": "1",\
"parent_id": "1",\
"name": "Прочитать документацию по Django",\
"description": "Oh! Django!",\
"starred": "1",\
"status": "skipped",\
"attachments": [],\
"context_id": [1],\
"start_date": "01.01.2010",\
"due_date": "31.01.2010",\
"complete_date": "01.03.2010"\
},{\
"id": "2",\
"parent_id": "2",\
"name": "Выбрать движок под zoldatoff.ru",\
"description": "A site about me...",\
"starred": "0",\
"status": "completed",\
"attachments": [],\
"context_id": [2],\
"start_date": "01.01.2010",\
"due_date": "31.01.2010",\
"complete_date": "01.03.2010"\
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

var folders_list = $.parseJSON(folder_list);
var projects_list = $.parseJSON(project_list);
var tasks_list = $.parseJSON(task_list);
var contexts_list = $.parseJSON(context_list);

function grepArray(list, p) {
	return $.grep(list, function(e, i) {
		var ret = true;
		
		if (p.name) ret = ret && (p.name == e.name);		
		if (p.id) ret = ret && (p.id == e.id);
		if (p.parent_id) ret = ret && (p.parent_id == e.parent_id);
		
		return ret;
	});
}

function parseStatus(status) {
	switch(status) {
		case "active": 
			return("c_task_active");
		case "skipped":	
			return("c_task_skipped");
		case "completed":
			return("c_task_done");
		default:
			return("");
	};
}

function parseStar(star) {
	switch(star) {
		case "1": 
			return("c_star_button_v");
		default:
			return("");
	};
}

function switchList1(type) {
	switch(type) {
		case "Folders":
			return(folders_list);
		case "Projects":
			return(projects_list);
		case "Contexts":
			return(contexts_list);
		case "Tasks":
			return(tasks_list);
		default:
			return(folders_list);
	}
}

function switchList2(type) {
	switch(type) {
		case "Folders":
			return(projects_list);
		case "Projects":
			return(tasks_list);
		case "Contexts":
			return(tasks_list);
		default:
			return(tasks_list);
	}
}

function genList1(list1, list2, p) {	
	var t = $("#main_list").empty();
	var el;
	var list, filtered_list;
	
	//Список 1-го уровня
	$.each(list1, function(ind, val) {
		var el = $("<div>")
			.append("<span class=c_list_label>▾</span>")
			.append("<input type='text' value='" + val.name + "' class='c_input_level1'/>")
			.append("<ul class='c_level2_list'>");
			
		//Список 2-го уровня
		list = grepArray(list2, {parent_id: val.id});
		el.children("ul.c_level2_list").genList2(list);
		
		//Раскрытие списка
		el.children("span.c_list_label").toggle(function() {
				el.children("ul.c_level2_list").show_list2();
			}, function() {
				el.children("ul.c_level2_list").hide_list2();
		});
		
		t.append(el);
	});
	
	// Левая панель
	genLeftList(switchList1(p.type), list2, p);
}

function genLeftList(list1, list2, p) {	
	$("#aside_l h2").text(p.type);
	var ul = $("#left_list").empty();
	
	$.each(list1, function(ind, val) {
		el = $("<li>").text(val.name);
		el.click(function(){
			filtered_list = grepArray(list1, {name: val.name});
			genList1(filtered_list, list2, {type: p.type, selected: val.name});
		});
		(val.name == p.selected) && el.addClass("selected");
		ul.append(el);
	});
}


$.fn.genList2 = function(list2, p) {
	var t = $(this).empty();
	
	$.each(list2, function(ind, val){
		var el = $("<li>")
			.append("<span class='c_star_button " + parseStar(val.starred) + "'>★ &nbsp;</span>")
			.append("<input type='text' value='" + val.name + "' class='c_input_level2 " + parseStatus(val.status) + "'/>")
			.append("<input type='text' value='" + val.due_date + "' class='c_input_date " + parseStatus(val.status) + "' />");
			
		var arr = [["Complete", "✓"], ["Delete", "✘"], ["Edit", "➜"], ["Attachment", "⌘"]]; 
		$.each(arr, function(i, v) {
			el.append("<span class='c_text_button' title= '" + v[0] + "'>" + v[1] + " &nbsp;</span>");
		});
		
		el.data("id", val.id).data("name", val.name);
		t.append(el);
	});
	
	return t;	
};

$.fn.hide_list2 = function() {
	$(this).slideDown("fast");
	$(this).siblings("span.c_list_label").text("▾");
};

$.fn.show_list2 = function() {
	$(this).slideUp("fast");
	$(this).siblings("span.c_list_label").text("▸");
};
