$(function() {
    var responsive = $('#responsive-menu');
    var menu = $('.top ul');

    $(responsive).on('click', function(e){
        e.preventDefault();
        menu.toggle();
    });

    $(window).resize(function(){
        var w = $(this).width();

        if(w > 800 && menu.is(':hidden')) {
            menu.removeAttr('style');
        }
    });

    $('.top ul li').on('click', function(e) {
        var w = $(window).width();
        if(w < 800 ) {
            menu.toggle();
        }
    });

    $('section[data-type="background"]').each(function(){
        var $bgobj = $(this); // assigning the object

        var didScroll = false
        $(document).scroll(function(){
            didScroll = true;
        });

        setInterval(function() {
            if (didScroll) {
                didScroll = false;
                handle_scroll();
            }
        }, 10);

        function handle_scroll() {
            // Scroll the background at var speed
            // the yPos is a negative value because we're scrolling it UP!
            var yPos = -($(window).scrollTop() / $bgobj.data('speed'));

            // Put together our final background position
            var coords = '50% '+ yPos + 'px';

            // Move the background
            $bgobj.css({ backgroundPosition: coords });
        };
    });
});