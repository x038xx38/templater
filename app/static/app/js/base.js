// (function($) {
//
// 	"use strict";
//
// 	var fullHeight = function() {
// 		$('.js-fullheight').css('height', $(window).height());
// 		$(window).resize(function(){
// 			$('.js-fullheight').css('height', $(window).height());
// 		});
//
// 		// $('#sidebarCollapse').on('click', function () {
//   		// 	$('#sidebar').toggleClass('active');
//   		// });
//
// 	};
// 	fullHeight();
// })(jQuery);

$(function() {

});


$(document).ready(function() {

    $('.js-fullheight').css('height', $(window).height());
    $(window).resize(function(){
        $('.js-fullheight').css('height', $(window).height());
    });

    $("#sidebarCollapse").on("click", function() {
        $("#sidebar").toggleClass("active");
    });

    $('.components li a').click(function(e) {
        // e.preventDefault();
        let $this = $(this);
        // let test = $this.text()
        // alert(test)
        let mainList = $this.closest('ul').each(function() {
            // alert($(this).html());
        });
        let subLists = mainList.children('li').children('ul');
        // alert(subLists.text())

        mainList.children('li').removeClass('active');
        mainList.children('a').removeClass('clicked');
        subLists.addClass('collapse');

        $this.parent().addClass('active');
        let current = $this.parent().find('a:first');
        if (current.attr('id'))
            localStorage.setItem("activeCol", current.attr('id'));

        let selectedSublist = $this.closest('li').children('ul')
        if (selectedSublist.hasClass('collapse'))
          selectedSublist.removeClass('collapse');
        else
          selectedSublist.addClass('collapse');
    });


    let last = localStorage.getItem("activeCol");

    $("a[id="+last+"]").closest('li').addClass('active');
    // $("a[id="+last+"]").addClass('clicked');
    let selectedSublist = $("a[id="+last+"]").closest('li').children('ul');
    if (selectedSublist.hasClass('collapse'))
        selectedSublist.removeClass('collapse');
    else
        selectedSublist.addClass('collapse');


  //when a collapse group is shown, save it as the active collapse group
  // $("#sidebarmenu").on("shown.bs.collapse", function() {
  //   var active = $("#sidebarmenu .show");
  //   // alert(active)
  //   var submenuActive = active.find(".show").attr("id");
  //   // alert(submenuActive)
  //   localStorage.setItem("activeCollapseGroup", active.attr("id"));
  //   if (submenuActive) {
  //     localStorage.setItem("activeCollapseGroupSubmenu", submenuActive);
  //   }
  // });
  //
  // $("#sidebarmenu").on("hidden.bs.collapse", function() {
  //   localStorage.removeItem("activeCollapseGroup");
  //   localStorage.removeItem("activeCollapseGroupSubmenu");
  // });
  // var last = localStorage.getItem("activeCollapseGroup");
  // var lastSubmenu = localStorage.getItem("activeCollapseGroupSubmenu");
  // if (last !== null) {
  //   //remove default collapse settings
  //   $("#sidebarmenu .panel-collapse").removeClass("show");
  //   //show the account_last visible group
  //   $("#" + last).addClass("show");
  //   if (lastSubmenu) {
  //     $("#" + last).find("#" + lastSubmenu).addClass("show");
  //   }
  // }
});
