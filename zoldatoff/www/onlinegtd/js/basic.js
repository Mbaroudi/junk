"use strict";

var ajax_path = '/a/'

$(document).ready(function(){
	
	var H = $("#wrapper").height();	
	$("#aside_l, #aside_r").height(H);
	$("#main_sec").height(H-22);
	
	
	/********************************************************************************/
	// Inbox
	$("#input_inbox")
		.focusin(function() {
			if ($(this).val() == "Inbox") {
				$(this).val("");
			}
		})
		.focusout(function() {
			if ($(this).val() == "") {
				$(this).val("Inbox");
			};
		});
		
	$("#inbox_form").submit(function(){
		var vl = $("#input_inbox").val();
		if (vl !== "Inbox") {
			$.getJSON(ajax_path + 'tasks', {action: 'create', name: vl}, cbTaskCreate);
		}
		$("#input_inbox").val("Inbox");
		return false;
	});
	
	/********************************************************************************/
	// Search
	$("#input_search")
		.focusin(function() {
			if ($(this).val() == "Search") {
				$(this).val("");
			}
		})
		.focusout(function() {
			if ($(this).val() == "") {
				$(this).val("Search");
			};
		});
		
	$("#search_form").submit(function(){
		$("#input_search").val("Search");
		return false;
	});
	
	/********************************************************************************/	
	// Left input: new Folder, Project, Task
	$("#left_control.add").toggle(function(){
		$("#left_form").show();
		$("#left_form input[type=text]").focus();
		$(this).text('—');		
	}, function(){
		$("#left_form").hide();
		$(this).text('+');
	});
	
	$("#left_form").submit(function(){
		var i = $("#left_form input[type=text]");
		if (i.val() !== "") {
			var type = $("#main_menu").data('selected')
			$.getJSON(ajax_path + type, {action: 'create', name: i.val()}, cbObjectCreate);
			i.val("");
			$("#left_control.add").click();
		}	
		return false;
	});
	
	/********************************************************************************/
	// Main menu	
	$("#folders, #projects, #contexts").click(function(){
		var type = $(this).attr("id")
		if ($("#main_menu").data('selected') !== type) {
			$("#main_menu")
				.data('selected', type)
				.children("li").removeClass("selected");
			$(this).addClass("selected");
		}
		genList1(switchList1(type), switchList2(type), {type: type});
		return false;
	});
	
	/********************************************************************************/	
	// Lists: Folders, Projects, Contexts, Tasks
	//$(".scrollable").scrollable({ vertical: true, mousewheel: false});	
	
	$("span.c_list_label").live("click", function(){
		var el = $(this).siblings("ul.c_level2_list");
		if (el.is(':visible')) {
			el.hide_list2();
		}
		else {
			el.show_list2();
		}
		return false;
	});
	
	$(".c_input_level1, .c_input_level2, .c_input_date")
		.live("focusin", function(){
			$(this).addClass("selected");
		})
		.live("focusout", function(){
			$(this).removeClass("selected");
		})
		.live("keydown", function(event){
	  		if (event.keyCode == 13){
	    		$(this).blur();
	  		}
		});
	
	$("span.c_text_button[title='Delete']").live("click", function(){
		$(this).parent("li").hide();
		//TODO: Поправить сам task
		return false;
	});
	
	$("span.c_text_button[title='Complete']").live("click", function(){
		var t = $(this);
		t.siblings().removeClass("c_task_active").removeClass("c_task_skipped");
		t.siblings(".c_input_level2").addClass("c_task_done");
		t.siblings(".c_input_date").addClass("c_task_done");
		t.html("☑ &nbsp;").attr("title", "Uncomplete");
		//TODO: Поправить сам task
		return false;
	});
	
	$("span.c_text_button[title='Uncomplete']").live("click", function(){
		var t = $(this);
		t.siblings().removeClass("c_task_done");
		t.html("✓ &nbsp;").attr("title", "Complete");
		//TODO: Поправить сам task, проставить правильный статус и обновить список
		return false;
	});
	
	$("span.c_star_button").live("click", function(){
		$(this).toggleClass("c_star_button_v");
		//TODO: Поправить сам task
		return false;
	});
	
	/********************************************************************************/
	// Query server data
	$.each(['contexts', 'folders'], function(i, type) {
		$.getJSON(ajax_path + type, {action: 'list'}, function(json) {
			list[type] = json;
			if ($("#main_menu").data('selected') == type) {
				genList1(switchList1(type), switchList2(type), {type: type});			
			}
		});
	});
	
	// Draw interface
	$("#folders").click(); //TODO: do smth else
	
});

function cbObjectCreate(json) {	
	var type = $("#main_menu").data('selected');
	$.merge(list[type], $.makeArray(json));
	genList1(switchList1(type), switchList2(type), {type: type});
}

function cbTaskCreate(json) {	
	var type = 'tasks';
	$.merge(list[type], $.makeArray(json));
	
	// При заведении новой задачи нужно учесть текущее представление
	type = switchType1(type);	
	
	genList1(switchList1(type), switchList2(type), {type: type});
}