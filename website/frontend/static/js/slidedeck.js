$(window).load(function(){
    $(".royalSlider").royalSlider({
        controlNavigation: 'none',
        fullscreen: {
          // fullscreen options go gere
          enabled: true,
          nativeFS: true
        },
        deeplinking: {
            // deep linking options go gere
            enabled: true,
            change: true,
            prefix: 'slide-'
        },
        arrowsNav: true,
        arrowsNavAutoHide: false,
        imageScalePadding: 0,
        slidesSpacing: 0,
        imageAlignCenter: false,
        imageScaleMode: 'fit',
        sliderDrag: false,
        navigateByClick: false,
        keyboardNavEnabled: true,
        fadeinLoadedSlide: false,
        addActiveClass: true,
        usePreloader: false
    });

    var slider = $(".royalSlider").data('royalSlider');

    function resize_player() {
      var slider_width = $(".royalSlider").width(),
          slider_height = $(".royalSlider").height(),
          ratio = $('.rsActiveSlide img').width() / $('.rsActiveSlide img').height();

      var margin_top = 0,
          margin_left = 0;
      if (!$('.royalSlider').hasClass('rsFullscreen')) {
        // slides width cannot be wider than 906px
        slider_width = Math.min(906, slider_width);
        // slides height cannot be taller than 510px, and also has to keep in ratio with 906px max width
        slider_height = (510 / 906) * slider_width;
        // whole slider needs to match the ratio of the image
        slider_width = slider_height * ratio;
      } else {
        // make the image fill the screen
        slider_height = $('.rsActiveSlide img').height();
        slider_width = slider_height * ratio;
        $('.rsOverflow').css('width', slider_width);
        // center vertically
        margin_top = Math.max(($(".royalSlider").height() - slider_height) / 2, 0);
      }

      // center horizontally
      margin_left =Math.max(($(".royalSlider").width() - slider_width) / 2, 0);

      $('.rsOverflow').css('width', slider_width);
      $('.rsOverflow').css('margin-top', margin_top);
      $('.rsOverflow').css('margin-left', margin_left);
      $('.royalSlider').css('height', slider_height);

      resize_textLayer();

      slider.updateSliderSize();
    }

    function resize_textLayer() {
      var slider_height = $(".royalSlider").height();

      $('.textLayer div').each(function() {
        var font_size = $(this).data('fontSize'),
            real_size = slider_height * (font_size / 100);

        $(this).css('font-size', real_size);
      });
    }

    if (slider) {
      var slideCountEl = $('<div class="rsNav rsBullets"></div>').appendTo( $(".rsOverflow") );

      function updCount() {
          slideCountEl.html( (slider.currSlideId+1) + ' of ' + slider.numSlides );
      }
      slider.ev.on('rsAfterSlideChange', updCount);
      updCount();

      // after first slide has been laoded
      slider.ev.on('rsMaybeSizeReady', function(e, slideObject) {
          if(slideObject.id === 0) {
              resize_player();
          }
      });
      // every time resizes
      slider.ev.on('rsOnUpdateNav', resize_player);
    }
});
