function cl(thing){
    console.log(thing);
}
function show_error(text){
    $('#js_error_noti').text(text).slideDown(500);
    setTimeout(function(){
        $('#js_error_noti').slideUp(500);
    }, 8000);
    scrollTo(0,0);
}
function show_success(text){
    $('#js_success_noti').text(text).slideDown(500);
    setTimeout(function(){
        $('#js_success_noti').slideUp(500);
    }, 8000);
    scrollTo(0,0);
}
function my_serialize(form){
    var n = [];
    var c = form.serialize().split('&');
    for(var i=0;i<c.length;i++){
        var e = c[i].split('=');
        if(e[1].length > 0){
            n.push(c[i]);
        }
    }
    return n.join('&');
}
function eid(id) {
    return document.getElementById(id);
}
function msieversion() {
        var ua = window.navigator.userAgent;
        var msie = ua.indexOf("MSIE ");
        if (msie > 0 || !!navigator.userAgent.match(/Trident.*rv\:11\./)){
            return parseInt(ua.substring(msie + 5, ua.indexOf(".", msie)));
        }
   return false;
}
function hasFlash() {
    return (typeof navigator.plugins != "undefined" && typeof navigator.plugins['Shockwave Flash'] != "undefined") || (typeof window.ActiveXObject != "undefined");
};

function html5video_codecs(){
    var testEl = document.createElement( "video" ), mpeg4, h264, ogg, webm;
    var supports = {'video/mp4':0,'video/ogg':0,'video/webm':0};
    if ( testEl.canPlayType ) {
        // Check for MPEG-4 support
        //supports['mpeg4'] = "" !== testEl.canPlayType( 'video/mp4; codecs="mp4v.20.8"' );

        // Check for h264 support
        supports['video/mp4'] = "" !== ( testEl.canPlayType( 'video/mp4; codecs="avc1.42E01E"' )
            || testEl.canPlayType( 'video/mp4; codecs="avc1.42E01E, mp4a.40.2"' ) );

        // Check for Ogg support
        supports['video/ogg'] = "" !== testEl.canPlayType( 'video/ogg; codecs="theora"' );

        // Check for Webm support
        supports['video/webm'] = "" !== testEl.canPlayType( 'video/webm; codecs="vp8, vorbis"' );
    }
    return supports;
}
jQuery(document).ready(function($) {
    //my radio buttons
    $('.my_radio').each(function(){
        var input = $(this).find('input');
        input.css('visibility','hidden');
        if(input.prop('checked')){
            $(this).addClass('my_radio_checked');
        }
    });
    $('.my_radio input').change(function(){
        $('input[name="'+ $(this).attr('name') + '"]').each(function(){
            if($(this).prop('checked')){
                $(this).closest('.my_radio').addClass('my_radio_checked');
            }else{
                $(this).closest('.my_radio').removeClass('my_radio_checked');
            }
        });
    });
    function init_my_checkboxes(area){
        // my checkboxes
        area.find('.my_checkbox').each(function(){
            var input = $(this).find('input');
            input.css('visibility','hidden');
            if(input.prop('checked')){
                $(this).addClass('my_checkbox_checked');
            }
        });
        area.find('.my_checkbox input').change(function(){
            if($(this).prop('checked')){
                $(this).closest('.my_checkbox').addClass('my_checkbox_checked');
            }else{
                $(this).closest('.my_checkbox').removeClass('my_checkbox_checked');
            }
        });
        area.find('.my_checkbox').on('click', function(){
            $(this).find('input').click();
        });
    }
    init_my_checkboxes($('body'));

    //home page
    $('.categoriesList a').on('click', function(e){
        e.preventDefault();
        var url = $(this).attr('href') + '?' + my_serialize($('#search_form'));
        if(e.which === 1){
            location.href = url;
        }else{
            window.open(url)
        }
        return false;
    });
    //captcha
    var refresh_send = false;
    $('.captchaRefresh').on('click', function(){
        var that = $(this);
        if(!refresh_send){
            refresh_send = true;
            $.get($(this).data('url'), function(data){
                that.prev('img').attr('src', data['image_url']);
                that.next('input').val(data['key']);
                refresh_send = false;
            },'json');
        }
    });
    //posting
    function in_datepicker(){
        $( "#datepicker" ).datepicker({
          onSelect: function(date){
            $('#datepicker+input').val(date);
          },
          dateFormat: "yy-mm-dd"
        });
    }
    if($( "#datepicker" ).length){
        in_datepicker();
    }
    var get_additional_fields = function(){
        var cat = $('#id_category').val();
        if(cat){
            sub_cat = $('#id_sub_category').val() || '0';
            $.get(APP.urls.get_fields.replace('222',sub_cat).replace('111', cat) + ($('#id_offering_0').prop('checked')?'?looking=1':""),
            function(data){
//                data = $.trim(data);
//                if(data){
                    $('#additional_fields').html(data);
                    in_datepicker();
                    init_my_checkboxes($('#additional_fields'));
//                }
            }, 'html');
        }
    };

    $('#post_ads_form #id_category').change(function(){
        get_additional_fields();
    });

    $('#post_ads_form #id_offering_0, #post_ads_form #id_offering_1').change(function(){
        $('#id_district').prop('required', ($(this).val() === "True")).prevAll('label').find('em').css('display', $(this).val() === "True" ? 'inline': 'none');
        get_additional_fields();
    });

    $(document).on('change', '#post_ads_form #id_sub_category', get_additional_fields);


    //search forms
    $('#search_form').on('submit', function(){
        location.href = $(this).attr('action') + '?' + my_serialize($(this));
        return false;
    });

    $('#search_form #id_category, #id_offering_0, #id_offering_1').change(get_additional_filters);

    function get_additional_filters(){
        $('#id_sub_category').remove();
        var cat = $('#search_form #id_category').val();
        if(cat){
            $.get(APP.urls.get_filters.replace('222','0').replace('111',cat)+($('#id_offering_1').prop('checked')?'?offering=1':""),
            function(data){
                $('#additional_filters').html(data);
                $('#sub_category_wraper').html($('#id_sub_category'));
            }, 'html');
        }else{
            $('#additional_filters').empty();
        }
    }
    var dist_required = false;
    var on_town_change = function(){
        var dist_select = $('#id_district');
        var first_opt = dist_select.find('option:first-child').clone();
        var value = dist_select.val();
        if(dist_select.css('display') !== 'none'){
            dist_required = dist_select.prop('required');
        }
        dist_select.empty().css('display', 'none').prop('required', false).closest('div').css('display', 'none');
        var town = $('#id_town').val();
        if(town){
            $.get(APP.urls.get_districts.replace('111',town),
            function(data){
                if(data){
                    dist_select.append(data).css('display', 'inline-block').val(value).prop('required', dist_required).closest('div').css('display', 'block');
                }
            }, 'html');
        }
        dist_select.html(first_opt);
    };
    $('#search_form #id_town, #post_ads_form #id_town').change(on_town_change);
    on_town_change();

    $('.filter_tabs>div').click(function(){
        var value = $(this).data('value');
        if(value){
            $(this).parent('div').find('input').attr('name', 'private').val(value);
        }else{
            $(this).parent('div').find('input').attr('name','').val('');
        }
        $(this).closest('.filter_tabs').find('.tab-active').removeClass('tab-active');
        $(this).addClass('tab-active').closest('form').submit();
    });
    ///search autocomplete
    var Autocomplete = function(options) {
        this.form_selector = options.form_selector;
        this.url = options.url || '/search/autocomplete/';
        this.delay = parseInt(options.delay || 300);
        this.minimum_length = parseInt(options.minimum_length || 3);
        this.form_elem = null;
        this.query_box = null;
    }
    Autocomplete.prototype.setup = function() {
        var self = this;
        this.results_wrapper = $('.ac-results');
        this.form_elem = $(this.form_selector);
        this.query_box = this.form_elem.find('input[name=q]');
        this.select_item = function(item){
            self.query_box.val(item.text());
            $('.ac-results').empty();
            return false;
        };
        // Watch the input box.
        this.query_box.on('keyup', function(e) {
            if ([13,38,40].indexOf(e.keyCode) < 0) {//NOT up, down, enter
                var query = self.query_box.val();
                if(query.length < self.minimum_length) {
                    return false;
                }
                self.fetch($(this).closest('form').serialize());
            }else{
                //get active item & new active item
                var item = self.results_wrapper.find('.active_option');
                if(item.length === 0){
                    item = self.results_wrapper.find('div');
                    if(item.length){
                        item = e.keyCode === 38 ? item.last() : item.first();
                    }
                }else if(e.keyCode !== 13){
                    item.removeClass('active_option');
                    if(e.keyCode === 38){
                        item = item.prevAll('div').length ? item.prevAll('div').first() : self.results_wrapper.find('div').last();
                    }else{
                        item = item.nextAll('div').length ? item.nextAll('div').first() : self.results_wrapper.find('div').first();
                    }
                }
//                if(item.length){
//                    item.addClass('active_option');
//                    if(e.keyCode === 13){
//                        self.select_item(item);
//                    }
//                }
            }
//        }).on('keydown', function(e){
//            if(e.keyCode === 13 && $('.ac-results .ac-result').length){
//                e.preventDefault();
//                return false;
//            }
        }).on('focus', function(){
            self.results_wrapper.show();
        }).on('blur', function(){
            setTimeout(function(){
                self.results_wrapper.hide();
            }, 100);
        });
        // On selecting a result, populate the search field.
        this.form_elem.on('mousedown', '.ac-result', function(ev) {
            self.select_item($(this));
        });
    }
    Autocomplete.prototype.fetch = function(data) {
        var self = this;
        $.ajax({
            url: this.url,
            data: data,
            success: function(data) {
                self.show_results(data);
            }
        });
    }

    Autocomplete.prototype.show_results = function(data) {
        // Remove any existing results.
        $('.ac-results').empty();
        var results = data.results || [];
        var base_elem = $('<div class="ac-result"></div>');
        if(results.length > 0) {
            for(var res_offset in results) {
              var elem = base_elem.clone();
              elem.text(results[res_offset]);
              this.results_wrapper.append(elem);
            }
        }
    }
    search_autocomplete = new Autocomplete({
        form_selector: '#search_form',
        url: APP.urls.search_autocomplete,
        minimum_length: 1,
    });
    search_autocomplete.setup()



    //display video player
    var ie_version = msieversion();
    var html5codecs = html5video_codecs();
    var flash = hasFlash();
    $('.video').each(function(){
        var type = $(this).data('type');
        if( flash && (!html5codecs[type]
            || (ie_version &&  type !== 'video/mp4' )
            || type === 'video/x-flv') ){
            jwplayer($(this).attr('id')).setup({
                file: $(this).data('url'),
                //image: "http://example.com/uploads/myPoster.jpg",
                width: 545,
                height: 400
            });
        }
    });

    // POSTING FORM
    if($('#id_address').length){
        var input = $('#id_address').get(0);
        $('#id_address').keydown(function(event){
            if(event.keyCode == 13) {
                event.preventDefault();
                return false;
            }
        });
        //address autocomplete
        var options = {
          types: ['geocode'],
          componentRestrictions: {country: 'ua'},
          location: new google.maps.LatLng( 50.006415,36.232116 ),
          radius:100000,
        };
        autocomplete = new google.maps.places.Autocomplete(input, options);

        google.maps.event.addListener(autocomplete, 'place_changed', function() {
            var place = autocomplete.getPlace();
            if(place.geometry !== undefined){
                setPosition(place.geometry.location);
            }
        });
        ///

        ////map
        var lat = $('#id_lat').val() || 50.006415;
        var lon = $('#id_lon').val() || 36.232116;
        var myLatlng = new google.maps.LatLng(lat, lon);
        var mapOptions = { zoom: 10,
                           center: myLatlng }
        var map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);

        google.maps.event.addListener(map, 'click', onReplaceMarker);
        var onReplaceMarker = function (event) {
             var geocoder = new google.maps.Geocoder();
             geocoder.geocode({
                 "latLng":event.latLng
             }, function (results, status) {
                 if (status == google.maps.GeocoderStatus.OK) {
                     var lat = results[0].geometry.location.lat(),
                         lng = results[0].geometry.location.lng(),
                         placeName = results[0].address_components[0].long_name,
                         latlng = new google.maps.LatLng(lat, lng);
                         setPosition(latlng);
                     $('#id_address').val(results[0].formatted_address);
                 }
             });
         };
        //marker
        var marker = new google.maps.Marker({
            position: myLatlng,
            map: map,
            title: 'Set Address'
        });
        marker.setDraggable (true);
        google.maps.event.addListener(marker, "dragend", onReplaceMarker);

        var setPosition = function(latlng){
            marker.setPosition(latlng);//move marker
            map.setCenter(latlng);
            map.setZoom(13);
            $('#id_lat').val(latlng.lat());
            $('#id_lon').val(latlng.lng());
        };
    }


    //UPLOAD PHOTOS
    var upload_container = eid('img_container');
    if(upload_container){
        var uploader = new plupload.Uploader({
            runtimes : 'html5,flash,silverlight,html4',
            browse_button : 'pickfiles', // you can pass in id...
            container: upload_container, // ... or DOM Element itself,
            drop_element: 'filelist',
            max_file_size : APP.settings.UPLOAD_IMG_MAX_SIZE,
            max_file_count: APP.settings.UPLOAD_IMAGES_LIMIT,

            url: APP.urls.image_upload,

            flash_swf_url : APP.urls.static + 'js/plupload/Moxie.swf',
            silverlight_xap_url : APP.urls.static + 'js/plupload/Moxie.xap',
            filters : [
                {title : "Image files", extensions : APP.settings.UPLOAD_IMAGES_TYPES},
//                {title : "Video files", extensions : "mp4,avi"}
            ],

            init: {
                PostInit: function(up) {
                    $('#filelist>.file_input').each(function(){
                        $(this).remove();
                    });
                    if ($('#filelist>div').length >= up.settings.max_file_count) {
                        $('#img_container').hide();
                    }
                    $('#filelist').prepend('<em class="clear"></em>');
                },

                FilesAdded: function(up, files) {

                    plupload.each(files, function(file) {
                        if ($('#filelist>.uploaded_file').length < up.settings.max_file_count) {
                            $('#filelist #img_container').before('<div class="uploaded_file" id="' + file.id + '"></div>');
                            uploader.start();
                        }
                        if ($('#filelist>.uploaded_file').length >= up.settings.max_file_count) {
                            $('#img_container').hide();
                        }
                        //eid('filelist').innerHTML += '<div id="' + file.id + '">' + file.name + ' (' + plupload.formatSize(file.size) + ') <b></b></div>';
                    });
                },
                FileUploaded: function(up, file, object){
                    try {
                        var resp = JSON.parse(object.response);
                    }
                    catch(err) {
                       resp = JSON.parse($(object.response).text());
                    }
                    if(resp.OK){
                         eid(file.id).innerHTML += '<input type="hidden" name="images[]" value="' + resp.id + '" />'+
                                                   '<img src="' + resp.url +'" />'+
                                                   '<div class="delete_img">×</div>';
                    }else{
                        $('#'+file.id).remove();
                    }
                },
//                UploadProgress: function(up, file) {
//                    eid(file.id).getElementsByTagName('b')[0].innerHTML = '<span>' + file.percent + "%</span>";
//                },
                Error: function(up, err) {
                    eid('console').innerHTML += "\nError #" + err.code + ": " + err.message;
                }
            }
        });
        uploader.init();
        $(document).on('click','#filelist .delete_img',function(){$('#img_container').show();$(this).parent('div').remove();});
        $(function() {
            $( "#filelist" ).sortable({items: '.uploaded_file'});
            $( "#filelist" ).disableSelection();
        });
	}
	//UPLOAD VIDEO
	var upload_video = eid('video_container');
    if(upload_video){

        var vid_uploader = new plupload.Uploader({
            runtimes : 'html5,flash,silverlight,html4',
            browse_button : 'pick_videos', // you can pass in id...
            container: upload_video, // ... or DOM Element itself
            max_file_size : APP.settings.UPLOAD_VIDEO_MAX_SIZE,
            max_file_count: APP.settings.UPLOAD_VIDEO_LIMIT,

            // Fake server response here
            // url : '../upload.php',
            url: APP.urls.video_upload,

            flash_swf_url : APP.urls.static + 'js/plupload/Moxie.swf',
            silverlight_xap_url : APP.urls.static + 'js/plupload/Moxie.xap',
            filters : [
                {title : "Video files", extensions : APP.settings.UPLOAD_VIDEO_TYPES}
            ],

            init: {
                PostInit: function(up) {
                    $('#video_list>.file_input').each(function(){
                        $(this).remove();
                    });
                    if ($('#video_list>.uploaded_file').length >= up.settings.max_file_count) {
                        $('#video_container').hide();
                    }
                    $('#video_list').append('<em class="clear"></em>');
                },
                FilesAdded: function(up, files) {
                    plupload.each(files, function(file) {
                        if ($('#video_list>.uploaded_file').length < up.settings.max_file_count) {
                            $('#video_list #video_container').before('<div class="uploaded_file" id="' + file.id + '"></div>');
                            vid_uploader.start();
                        }
                        if ($('#video_list>.uploaded_file').length >= up.settings.max_file_count) {
                            $('#video_container').hide();
                        }
                    });
                },
                FileUploaded: function(up, file, object){
                    try {
                        var resp = JSON.parse(object.response);
                    }
                    catch(err) {
                       resp = JSON.parse($(object.response).text());
                    }
                    if(resp.OK){
                        eid(file.id).innerHTML +=
                        '<input type="hidden" name="video[]" value="' + resp.id + '" />'+
                        '<em class="sprite ico_video"></em><div class="text">'+ resp.name +
                        '</div><div class="delete_img">×</div>';
                    }else{
                        $('#'+file.id).remove();
                        cl(resp.error.join('\n'));
                    }
                },
//                UploadProgress: function(up, file) {
//                    eid(file.id).getElementsByTagName('b')[0].innerHTML = '<span>' + file.percent + "%</span>";
//                },
                Error: function(up, err) {
                    eid('video_console').innerHTML += "\nError #" + err.code + ": " + err.message;
                }
            }
        });
        vid_uploader.init();
        $(document).on('click','#video_list .delete_img',function(){$('#video_container').show();$(this).parent('div').remove();$('#video_container').show();});
	}






	/** DETAILS PAGE **/
    $("#gallery_output img").not(":first").hide();
    $("#gallery a").click(function() {
        if ( $("#" + this.rel).is(":hidden") ) {
            $("#gallery a").removeClass('active');
            $(this).addClass('active');
            $("#gallery_output img").slideUp();
            $("#" + this.rel).slideDown();
        }
    });

    var static_map = $('#static_map');
    if(static_map.length){
        var lat = parseFloat(static_map.data('lat').replace(',','.')) || 50.006415;
        var lon = parseFloat(static_map.data('lon').replace(',','.')) || 36.232116;
        var myLatlng = new google.maps.LatLng(lat, lon);
        var map = new google.maps.Map(static_map.get(0), { zoom: 13, center: myLatlng });
        //marker
        var marker = new google.maps.Marker({
            position: myLatlng,
            map: map,
            title: 'Address'
        });
    }
    var acc_opened = 0;


    $('.acc_header').on('click', function(){
        var body = $(this).next('.acc_body');
        if(acc_opened){
            body.stop().slideUp();
            acc_opened = 0;
        }else{
            body.stop().slideDown();
            acc_opened = 1;
        }
    });

    function show_input_error(obj){
        var from = '#ea7777';
        if(!obj.data('bg')){
            obj.data('bg', obj.css('backgroundColor'));
        }
        obj.stop().css('backgroundColor', from).animate({'backgroundColor': obj.data('bg')}, 1000, function(){
            obj.css('backgroundColor', obj.data('bg'));
        });
    }

    $('#sendToFriendForm').on('submit', function(e){
        e.preventDefault();
        var email = $(this).find("#id_email");
        var email_val = $.trim(email.val());
        if(email_val && new RegExp(/^[^@]+@[^@]+\.[^@]{2,}$/).test(email_val)){

            $.post(APP.urls.send_to_friend,
            {csrfmiddlewaretoken: $(this).find("[name='csrfmiddlewaretoken']").val(),
            ad_id: $(this).find("#id_ad_id").val(),
            email: email_val},
            function(data){
                if('error' in data){
                    show_error(data['error']);
                }else{
                    show_success('Email sent successfully');
                }
                $("#id_email").val("");
                $('.acc_heade').click();
            }, 'json');

        }else{
            show_input_error(email);
            $(this).find("#id_email").val(email_val);
        }
        return false;
    });

    /** PROFILE **/
//    $('.disableAd').on('click', function(){
//        $.get(APP.urls.get_fields.replace('222',$(this).val()).replace('111',$('#id_category').val()),
//        function(data){
//            data = $.trim(data);
//            cl(data);
//            if(data){
//                $('#additional_fields').html(data);
//            }
//        }, 'html');
//    });
    /** --PROFILE **/

    //** FEEDBACK **//
    $('#feedbackModal .feedbackClose, #feedbackToggle').click(function(){
        $('#feedbackModal').toggle();
    });
    $('#feedbackModal form').submit(function(e){
        $(this).find('select, textarea').each(function(){
            $(this).removeClass('parsley-error');
            if(! $(this).val() ){
                $(this).addClass('parsley-error');
                setTimeout(function(){
                    $(this).removeClass('parsley-error');
                }, 2000);
                e.preventDefault();
                return false;
            }
        });
    });
    $('#feedbackModal select, #feedbackModal textarea').on('input change', function(){$(this).removeClass('parsley-error');});
    //** FEEDBACK **//

    /// SERVER FORM ERRORS
    $('input, textarea').on('input',  function(){
        $(this).nextAll('.errorlist').remove();
    });
    // ALERT DISMISS
    $(document).on('click', '.onchange_alert .alert_close', function(){
        $(this).closest('.onchange_alert').slideUp(200);
    });

    //$('.onchange_form').parsley({ successClass: 'alert', errorClass: 'alert-error' });
//    window.ParsleyConfig = {
//      errorsWrapper: '<ul class="errorlist"></ul>',
//      errorTemplate: '<li></li>'
//    };
});