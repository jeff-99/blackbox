(function(window,$){
     window.cur_pos = {};
     var eventOutputContainer = document.getElementById("event");

     var evtSrc = null;
     $('.event').on('create', function(){
        var event = $(this);
        evtSrc = new EventSource(event.data('stream'));

        evtSrc.addEventListener('measurement', function(e) {
            var data = JSON.parse(e.data);

            window.cur_pos =  {
               lat : parseFloat(data['latitude']),
               lng : parseFloat(data['longitude'])
            };

            $('.event').trigger('update', data);
        });

        evtSrc.onerror = function(e){console.log('error');console.log(e);};
        evtSrc.onopen = function(e){console.log('open');console.log(e);};

     }).on('shutdown', function(){
        console.log('shutting down!')
        evtSrc.close();
     }).on('update', function(e, data){
        var event = $(this);
        var gpsContainer = event.find('#gps');
        if(gpsContainer.length){
            gpsContainer.html(data['latitude'] + " " + data['longitude']);
        }

        var speedContainer = event.find('#speed');
        if(speedContainer.length){
            speedContainer.html(data["speed"]);
        }

        var angleContainer = event.find('#angle');
        if(angleContainer.length){
            angleContainer.html(data["angle"]);
        }


     }).on('click', '#stop',function(){
        $('.event').trigger('shutdown');
     }).trigger('create');



    $('.refresh').on('click' ,function(){
            console.log('hier');
            console.log(window.cur_pos);
            var map = new google.maps.Map( document.getElementById('map'),{zoom:16,center:window.cur_pos});
            console.log(map);
            var marker = new google.maps.Marker({
                position: window.cur_pos,
                map: map
            });
            console.log(marker);
    });
})(window,jQuery);