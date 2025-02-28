$(function(){
	$('#wizard').steps({
        headerTag: 'h4',
        bodyTag: 'section',
        transitionEffect: 'fade',
        enableAllSteps: true,
        transitionEffectSpeed: 500,
        onInit: function (event, currentIndex) {
            $('#wizard').find('a[href="#next"]').addClass('btn').addClass('btn-primary');
            $('#wizard').find('a[href="#previous"]').addClass('btn').addClass('btn-primary');
            $('#wizard').find('a[href="#finish"]').addClass('btn').addClass('btn-primary');
            $('.steps ul').width(440)
        },
        onStepChanging: function (event, currentIndex, newIndex) {
            if ( newIndex === 0 ) {
                $('.steps ul').attr('data-content', '');
                console.log('Шаг 0')
            }

            if ( newIndex === 1 ) {
                $('.steps ul').addClass('step-2');
                console.log('Шаг 1')
            } else {
                $('.steps ul').removeClass('step-2');
            }

            if ( newIndex === 2 ) {
                console.log('Шаг 2')
                var chk = $("input:checked").val()
                console.log(chk)
                dataToSend = {
                    'member_id': chk.toString(),
                    'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val(),
                }
                $.ajax({
                    url: '/app/member/land',
                    type: 'POST',
                    data: dataToSend,
                    dataType: 'json',
                    beforeSend: function (){
                        $('#wizard-p-1').html('<p style="text-align: center"> Идет поиск земельных участков ... </p>');
                    },
                    complete: function (){

                    },
                    success: function (data) {
                        var table = $('<table>').addClass('table table-hover mt-3 table-sm text-muted table-bordered');
                        table.append('<thead><tr>' +
                            '<th scope="col" style="border-bottom: 0px; text-align: center">№</th>' +
                            '<th scope="col" style="border-bottom: 0px;" class="w-25">Кадастровый номер</th>' +
                            '<th scope="col" style="border-bottom: 0px;" class="w-75">Адрес</th>' +
                            '<th scope="col" style="border-bottom: 0px;"></th></tr></thead>')
                        table.append('<tbody>')
                        for(i=0; i<data['data'].length; i++){
                            var checked = (i === 0) ? 'checked' : '';
                            var row = $('<tr>').append(
                                '<td>'+(i+1)+'</td>' +
                                '<td>'+data['data'][i]['kadastr_number']+'</td>' +
                                '<td>'+data['data'][i]['address']+'</td>' +
                                '<td align="center"><input type="radio" name="land_id" ' +
                                'value="'+data['data'][i]['id']+'"' + checked + '></td>');
                            table.append(row);
                        }
                        table.append('</tbody>')
                        $('#wizard-p-1').html('<h4>Земельные участки</h4>').append(table);


                        for(i=0; i<data['data'].length; i++) {
                            console.log(data['data'][i]['address'])
                        }

                    },
                    // error: ajaxLoadError
                });

                $('.steps ul').addClass('step-last');
            } else {
                $('.steps ul').removeClass('step-last')
            }
            return true; 
        },
        onFinished: function (event, currentIndex) {
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
