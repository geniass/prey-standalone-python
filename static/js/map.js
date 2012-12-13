var map;

jQuery(function($) {
    $(document).ready(function() {
        var latlng = new google.maps.LatLng(-34.397, 150.644);
        var myOptions = {
            zoom: 8,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
        console.dir(map);
        google.maps.event.trigger(map, 'resize');

        $('a[href="#profile"]').on('shown', function(e) {
            google.maps.event.trigger(map, 'resize');
        });
        //$("#map_canvas").css("width", 400).css("height", 400);
    });

    $(window).resize(function () {
        var h = $(window).height(),
        offsetTop = 60; // Calculate the top offset

    $('#map_canvas').css('height', (h - offsetTop));
    }).resize();

    $('a[href="#"]').click(function(){
        id = $(this).attr('id')
        alert(id);
        $.get("../.." + "/getreport" + "?id=" + id, function(data,status){
            alert(data);
            //update map
        });
    });

});

