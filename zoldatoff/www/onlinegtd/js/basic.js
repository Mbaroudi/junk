"use strict";

var ajax_path = '/a/'

$(document).ready(function(){
	
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
		
	$("#ok_inbox").click(function(){
		/*var el, vl;
		vl = $("#input_inbox").val();
		if (vl !== "Inbox") {
			el = $("<li>").append(vl);
			$("ul.c_task_list:first").append(el);
		}*/
	});
	
	// Search
	$("#input_search")
		.focusin(function() {
			if ($(this).val() == "Поиск") {
				$(this).val("");
			}
		})
		.focusout(function() {
			if ($(this).val() == "") {
				$(this).val("Поиск");
			};
		});
		
	// Lists: Folders, Projects, Contexts, Tasks
	$(".scrollable").scrollable({ vertical: true, mousewheel: false});	
	
	$(".c_input_level1, .c_input_level2, .c_input_date")
		.live("focusin", function(){
			$(this).css("border-color", "#494a3f");
		})
		.live("focusout", function(){
			$(this).css("border-color", "transparent");
		})
		.live("keydown", function(event){
	  		if (event.keyCode == 13){
	    		$(this).blur();
	  		}
		});
	
	$("span.c_text_button[title='Delete']").live("click", function(){
		$(this).parent("li").hide();
		//TODO: Поправить сам task
	});
	
	$("span.c_text_button[title='Complete']").live("click", function(){
		var t = $(this);
		t.siblings().removeClass("c_task_active").removeClass("c_task_skipped");
		t.siblings(".c_input_level2").addClass("c_task_done");
		t.siblings(".c_input_date").addClass("c_task_done");
		t.html("☑ &nbsp;").attr("title", "Uncomplete");
		//TODO: Поправить сам task
	});
	
	$("span.c_text_button[title='Uncomplete']").live("click", function(){
		var t = $(this);
		t.siblings().removeClass("c_task_done");
		t.html("✓ &nbsp;").attr("title", "Complete");
		//TODO: Поправить сам task, проставить правильный статус и обновить список
	});
	
	$("span.c_star_button").live("click", function(){
		$(this).toggleClass("c_star_button_v");
		//TODO: Поправить сам task
	});
		
	// Left input: new Folder, Project, Task
	$("#left_control.add").toggle(function(){
		$("#left_form").show();
		$("#left_form input[type=text]").focus();
		$(this).text('-');		
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
	
	// Main menu	
	$("#folder, #project, #context").click(function(){
		var type = $(this).attr("id")
		if ($("#main_menu").data('selected') !== type) {
			$("#main_menu")
				.data('selected', type)
				.children("li").removeClass("selected");
			$(this).addClass("selected");
		}
		genList1(switchList1(type), switchList2(type), {type: type});
	});
	
	/*$("#projects").click(function(){
		if ($("#main_menu").data('selected') !== "project") {
			$("#main_menu")
				.data('selected', "project")
				.children("li").removeClass("selected");
			$(this).addClass("selected");
		}
		genList1(projects_list, tasks_list, {type: "project"});
	});
	
	$("#contexts").click(function(){
		if ($("#main_menu").data('selected') !== "context") {
			$("#main_menu")
				.data('selected', "context")
				.children("li").removeClass("selected");
			$(this).addClass("selected");
		}
		genList1(contexts_list, tasks_list, {type: "context"});
	});*/
	
	// Query server data
	$.getJSON(ajax_path + 'context', {action: 'list'}, function(json) {
		contexts_list = json;
	});
	$.getJSON(ajax_path + 'folder', {action: 'list'}, function(json) {
		folders_list = json;
	});
	//TODO: get folders, projects, tasks
	
	// Draw interface
	$("#folders").click(); //TODO: do smth else
	
});

function cbObjectCreate(json) {	
	$.merge(contexts_list, $.makeArray(json));
	genList1(contexts_list, tasks_list, {type: "context"});
}