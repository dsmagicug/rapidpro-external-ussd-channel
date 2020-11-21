(function($) {

    var form = $("#config-form");
    form.validate({
        errorPlacement: function errorPlacement(error, element) {
             element.before(error); 
        },
        rules: {
            send_url : {
                required: true,
            },
            rapidpro_receive_url : {
                required: true,
            },
        },
        messages: {
            send_url : {
                required : "Please provide a correct domain here to continue (Must be a valid url)"
            },
            rapidpro_receive_url : {
                required : "please provide a valid URL like (http://domain.com)"
            },
        },
        onfocusout: function(element) {
            $(element).valid();
        },
        highlight : function(element, errorClass, validClass) {
            $(element).parent().parent().find('.form-group').addClass('form-error');
            $(element).removeClass('valid');
            $(element).addClass('error');
        },
        unhighlight: function(element, errorClass, validClass) {
            $(element).parent().parent().find('.form-group').removeClass('form-error');
            $(element).removeClass('error');
            $(element).addClass('valid');
        }
    });
    form.steps({
        headerTag: "section",
        bodyTag: "fieldset",
        transitionEffect: "fade",
        labels: {
            previous : 'Previous',
            next : 'Next',
            finish : 'Finish',
            current : ''
        },
        titleTemplate : '<section class="title">#title#</section>',
        onInit : function (event, currentIndex) { 
            // Suppress (skip) "Warning" step if the user is old enough.
            if(currentIndex === 0) {
                form.find('.actions').addClass('test');
            }
        },
        onStepChanging: function (event, currentIndex, newIndex)
        {
            form.validate().settings.ignore = ":disabled,:hidden";
            $("#send-value").html($("#id_send_url").val())
            $("#receive-value").html($("#id_rapidpro_receive_url").val())
            $("#timeout-value").html($("#id_timeout_after").val())
            $("#trigger_word-value").html($("#id_trigger_word").val())
            $("#trigger_country-value").html($("#id_country").val())


            return form.valid();
        },
        onFinishing: function (event, currentIndex)
        {
            form.validate().settings.ignore = ":disabled";
            console.log(form.serializeArray())
            form.submit();
            return form.valid();
        },
        onFinished: function (event, currentIndex)
        {

        },
        onStepChanged: function (event, currentIndex, priorIndex)
        {

         
        }
    });

    jQuery.extend(jQuery.validator.messages, {
        required: "",
        remote: "",
        email: "",
        url: "",
        date: "",
        dateISO: "",
        number: "",
        digits: "",
        creditcard: "",
        equalTo: ""
    });

    // $('#country').parent().append('<ul id="newcountry" class="select-list" name="country"></ul>');
    // $('#country option').each(function(){
    //     $('#newcountry').append('<li value="' + $(this).val() + '">'+$(this).text()+'</li>');
    // });
    // $('#country').remove();
    // $('#newcountry').attr('id', 'country');
    // $('#country li').first().addClass('init');
    // $("#country").on("click", ".init", function() {
    //     $(this).closest("#country").children('li:not(.init)').toggle();
    // });
    
    // var allOptions = $("#country").children('li:not(.init)');
    // $("#country").on("click", "li:not(.init)", function() {
    //     allOptions.removeClass('selected');
    //     $(this).addClass('selected');
    //     $("#country").children('.init').html($(this).html());
    //     allOptions.toggle();
    // });

    // var inputs = document.querySelectorAll( '.inputfile' );
	// Array.prototype.forEach.call( inputs, function( input )
	// {
	// 	var label	 = input.nextElementSibling,
	// 		labelVal = label.innerHTML;

	// 	input.addEventListener( 'change', function( e )
	// 	{
	// 		var fileName = '';
	// 		if( this.files && this.files.length > 1 )
	// 			fileName = ( this.getAttribute( 'data-multiple-caption' ) || '' ).replace( '{count}', this.files.length );
	// 		else
	// 			fileName = e.target.value.split( '\\' ).pop();

	// 		if( fileName )
	// 			label.querySelector( 'span' ).innerHTML = fileName;
	// 		else
	// 			label.innerHTML = labelVal;
	// 	});

	// 	// Firefox bug fix
	// 	input.addEventListener( 'focus', function(){ input.classList.add( 'has-focus' ); });
	// 	input.addEventListener( 'blur', function(){ input.classList.remove( 'has-focus' ); });
    // });
    
    
})(jQuery);
function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('.your_picture_image')
                .attr('src', e.target.result);
        };

        reader.readAsDataURL(input.files[0]);
    }
}
