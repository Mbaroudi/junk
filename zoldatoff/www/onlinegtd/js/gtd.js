"use strict";

var project_list = '[{\
"id": "0",\
"parent_id": "22",\
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
"parent_id": "23",\
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
"parent_id": "23",\
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
"parent_id": "22",\
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
"parent_id": "3",\
"name": "Купить герметик и водостойкий клей",\
"description": "3 герметика и 1 клей",\
"starred": "0",\
"status": "active",\
"attachments": [],\
"context_id": [15],\
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
"context_id": [14],\
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
"context_id": 13,\
"start_date": "01.01.2010",\
"due_date": "31.01.2010",\
"complete_date": "01.03.2010"\
}]';

var list = Object()
list.tasks = Array()
list.projects = $.parseJSON(project_list);
list.tasks = $.parseJSON(task_list);
list.contexts = Array()

function grepArray(list, p) {
	return $.grep(list, function(e, i) {
		var ret = true;
		
		if (p.name) ret = ret && (p.name == e.name);		
		if (p.id) ret = ret && (p.id == e.id);
		if (p.parent_id) ret = ret && (p.parent_id == e.parent_id);
		if (p.context_id) ret = ret && (p.context_id == e.context_id);
		
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
		case "tasks":
			return(list[$("#main_menu").data('selected')]);
		default:
			return(list[type]);
	}
}

function switchList2(type) {
	switch(type) {
		case "folders":
			return(list.projects);
		default:
			return(list.tasks);
	}
}

function switchType1(type) {
	switch(type) {
		case "tasks":
			return($("#main_menu").data('selected'));
		default:
			return("tasks");
	}
}

function switchType2(type) {
	switch(type) {
		case "folders":
			return("projects");
		default:
			return("tasks");
	}
}

function genList1(list1, list2, p) {	
	//$(".scrollable").data("scrollable").begin(0);
	
	var t = $("#main_list").empty();
	var l, filtered_list;
	
	//Список 1-го уровня
	$.each(list1, function(ind, val) {
		var el = $("<div class=item>")
			.append("<span class=c_list_label>↓</span>")
			.append("<input type='text' value='" + val.name + "' class='c_input_level1'/>")
			.append("<ul class='c_level2_list'>");
			
		//Список 2-го уровня
		switch(p.type) {
			case "contexts": 
				l = grepArray(list2, {context_id: val.id});
				break;
			default:
				l = grepArray(list2, {parent_id: val.id});
		}
		
		el.children("ul.c_level2_list").genList2(l, switchType2(p.type));
		
		t.append(el);
	});
	
	// Левая панель
	genLeftList(switchList1(p.type), list2, p);
}

function genLeftList(list1, list2, p) {	
	$("#aside_l h2").text(p.type);
	var ul = $("#left_list").empty();
	var el;
	
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
	var el, arr;
	
	$.each(list2, function(ind, val){
		el = $("<li>")
			.append("<span class='c_star_button " + parseStar(val.starred) + "'>★</span>")
			.append("<input type='text' value='" + val.name + "' class='c_input_level2 " + parseStatus(val.status) + "'/>")
			.append("<input type='text' value='" + val.due_date + "' class='c_input_date " + parseStatus(val.status) + "' />");
			
		switch (val.status) {
			case 'completed':
				arr = [["Uncomplete", "☑"], ["Delete", "✘"], ["Edit", "➜"], ["Attachment", "⌘"]]; 
				break;
			default:
				arr = [["Complete", "✓"], ["Delete", "✘"], ["Edit", "➜"], ["Attachment", "⌘"]]; 
		}
		
		$.each(arr, function(i, v) {
			el.append("<span class='c_text_button' title= '" + v[0] + "'>" + v[1] + " &nbsp;</span>");
		});
		
		el.data("id", val.id);
		t.append(el);
	});
	
	return t;	
};

$.fn.show_list2 = function() {
	$(this).slideDown("fast");
	$(this).siblings("span.c_list_label").text("↓");
	return $(this);
};

$.fn.hide_list2 = function() {
	$(this).slideUp("fast");
	$(this).siblings("span.c_list_label").text("→");
	return $(this);
};
