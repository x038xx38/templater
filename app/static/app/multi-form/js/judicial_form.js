$(function(){
	$("#wizard").steps({
        headerTag: "h4",
        bodyTag: "section",
        transitionEffect: "fade",
        enableAllSteps: false,
        transitionEffectSpeed: 500,

        onInit: function (event, currentIndex) {
            $("#wizard").find('a[href="#next"]').addClass('btn').addClass('btn-primary');
            $("#wizard").find('a[href="#previous"]').addClass('btn').addClass('btn-primary');
            $("#wizard").find('a[href="#finish"]').addClass('btn').addClass('btn-primary');
            $('.steps ul').width(440)
        },
        onStepChanging: function (event, currentIndex, newIndex) {

            if ( newIndex === 0 ) {
                //console.log('Шаг 1 :: Выбор судебного взыскания');
								return true;
            }
            if ( newIndex === 1 ) {
								let chk = $("input[name='options']:checked").val()
                //console.log('Шаблон судебного взыскания выбран под номером - ' + chk)
                //console.log('Шаг 2 :: Выбор должника');
                $('.steps ul').addClass('step-1');
								return true;
            } else {
                $('.steps ul').removeClass('step-1');
            }
            if ( newIndex === 2 ) {
                //console.log('Шаг 3 :: Выбор участков');
                let member_id = $("input[name='member_id']:checked").val();
								//console.log('Идентефикатор должника - ' + member_id)
                let dataToSend = {
                    'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val(),
                }
								let url = '/app/get-debit-land/' + member_id;
								$.ajax({
                    url: url,
                    type: 'POST',
                    data: dataToSend,
                    beforeSend: function (){
                        $('#wizard-p-2').html('<p style="text-align: center"> Поиск земельных участков ... </p>');
                    },
                    complete: function (){},
                    success: function (data) {
												//console.log(data)
												$('#wizard-p-2').html(data);
                    },
								});
               	$('.steps ul').addClass('step-2');
								//$('.steps ul').css('display', 'none')
								return true;
            } else {
                $('.steps ul').removeClass('step-2');
            }
						if ( newIndex === 3 ) {
                //console.log('Шаг 4 :: Определение участка суда');
								//$('.steps ul').hide();

                let member_id = $("input[name='member_id']:checked");
                let sum;
                if (member_id.length){
                    let tds = member_id.closest('tr').find('td');
                    sum = tds.eq(2).text();
                }

                dataToSend = {
                    'member_id': member_id.val(),
                    'summa': sum,
                    'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val(),
                }
                let url = '/app/findcourt';

                $.ajax({
                    url: url,
                    type: 'POST',
										//async: false,
                    // contentType: 'application/json; charset=utf-8',
                    data: dataToSend,
                    // dataType: 'json',
                    // async: false,
                    beforeSend: function (){
                        $('#wizard-p-3').html('<p style="text-align: center"> Идет поиск судебных участков ... </p>');
                    },
                    complete: function (){
											 	//$('.steps ul').addClass('step-4');
												//return true;
                    },
                    success: function (data) {
											//$('#wizard-p-2').html('<h4>Судебные участки</h4>').append(data);
											$('#wizard-p-3').html(data);
											//console.log(data)

											$('#result tr').each(function() {
                            if ($(this).find('input').is(':checked')){
                                var court_name = $(this).find('td').eq(0).html();
                                var input = $('<input>')
                                        .attr('type', 'hidden')
                                        .attr('name', 'court_name').val(court_name);
                                $('#form').append(input);
                                var court_address = $(this).find('td').eq(1).html();
                                var input = $('<input>')
                                        .attr('type', 'hidden')
                                        .attr('name', 'court_address').val(court_address);
																$('#form').append(input);
																var court_phone = $(this).find('td').eq(2).html();
                                var input = $('<input>')
                                        .attr('type', 'hidden')
                                        .attr('name', 'court_phone').val(court_phone);
                                $('#form').append(input);
                                console.log(court_name + ' ' + court_address)
                            }
                        });

                    },
                    // error: ajaxLoadError
                });
								return true;
            } else {
                $('.steps ul').removeClass('step-3');
            }
						///return false;
        },
        onFinished: function (event, currentIndex) {
            let chk = $("input[name='options']:checked").val()
            if ( chk === '1' ){
                $('#form').attr('action', '/app/isk_tmp/1')
            } else {
                $('#form').attr('action', '/app/isk_tmp/2')
            }
            $('#form').submit();
        },
        labels: {
            finish: "Сгенерировать",
            next: "Далее",
            previous: "Назад"
        }
    });
    // Custom Steps Jquery Steps
    $('.wizard > .steps li a').click(function(){
			$(this).parent().addClass('checked');
			$(this).parent().prevAll().addClass('checked');
			$(this).parent().nextAll().removeClass('checked');
    });
    // Custom Button Jquery Steps
    $('.forward').click(function(){
    	$("#wizard").steps('next');
    })
    $('.backward').click(function(){
        $("#wizard").steps('previous');
    })
    // Checkbox
    $('.checkbox-circle label').click(function(){
        $('.checkbox-circle label').removeClass('active');
        $(this).addClass('active');
    })
})
