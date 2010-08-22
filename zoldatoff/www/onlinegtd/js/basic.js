"use strict";

$(document).ready(function(){
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
	
	/* $(".c_text_button[title]").tooltip({ position: "bottom center" }); */
	$(".scrollable").scrollable({ vertical: true, mousewheel: false});	
	
	$(".c_input_folder, .c_input_project, .c_input_date")
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
	
	$("#folders").click(function(){
		if ($("#main_menu").data('selected') !== "folders") {
			$("#main_menu")
				.data('selected', "folders")
				.children("li").removeClass("selected");
			$(this).addClass("selected");
		}
		genList1(folders_list, projects_list, {type: "Folders"});
	});
	
	$("#projects").click(function(){
		if ($("#main_menu").data('selected') !== "projects") {
			$("#main_menu")
				.data('selected', "projects")
				.children("li").removeClass("selected");
			$(this).addClass("selected");
		}
		genList1(projects_list, tasks_list, {type: "Projects"});
	});
	
	$("#contexts").click(function(){
		if ($("#main_menu").data('selected') !== "contexts") {
			$("#main_menu")
				.data('selected', "contexts")
				.children("li").removeClass("selected");
			$(this).addClass("selected");
		}
		genList1(contexts_list, tasks_list, {type: "Contexts"});
	});
	
	$("#ok_inbox").click(function(){
		/*var el, vl;
		vl = $("#input_inbox").val();
		if (vl !== "Inbox") {
			el = $("<li>").append(vl);
			$("ul.c_task_list:first").append(el);
		}*/
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
		//TODO: Поправить сам task
	});
	
	$("#folders").click();
	
});