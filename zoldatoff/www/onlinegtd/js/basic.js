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
	
	/* */$(".c_text_button[title]").tooltip({ position: "bottom center" });
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
	
	/* */ $("#ok_inbox").click(function(){
		/*var el, vl;
		vl = $("#input_inbox").val();
		if (vl !== "Inbox") {
			el = $("<li>").append(vl);
			$("ul.c_task_list:first").append(el);
		}*/
		$("#folder_list").gen_folderlist($.parseJSON(folder_list));
	});
	
});