
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

        geocoder = new google.maps.Geocoder();
        infowindow = new google.maps.InfoWindow();

        $('a[href="#profile"]').on('shown', function(e) {
            google.maps.event.trigger(map, 'resize');
        });
        //$("#map_canvas").css("width", 400).css("height", 400);
    });

    $(window).resize(function () {
        var h = $(window).height(),
        offsetTop = 60; // Calculate the top offset

    //$('#map_canvas').css('height', (h - offsetTop));
    }).resize();

    $('a[href="#"]').click(function(){
        id = $(this).attr('id')
        //alert(id);
    $.get("../.." + "/getreport" + "?id=" + id, function(data,status){
        //alert(data['latitude']);
        report_data = data;
        //update map
        marker = new google.maps.Marker({
            position: new google.maps.LatLng(data['latitude'], data['longitude']),
               title:"Last Known Position"
        });
        marker.setMap(map);
        map.setCenter(new google.maps.LatLng(data['latitude'], data['longitude']));

        codeLatLng();
    });
    });

    function codeLatLng() {
        var latlng = new google.maps.LatLng(report_data['latitude'], report_data['longitude']);
        geocoder.geocode({'latLng': latlng}, function(results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                if (results[1]) {
                    map.setZoom(11);
                    marker = new google.maps.Marker({
                        position: latlng,
                           map: map
                    });
                    infowindow.setContent(results[1].formatted_address);
                    infowindow.open(map, marker);
                }
            } else {
                alert("Geocoder failed due to: " + status);
            }
        });
    }

});

