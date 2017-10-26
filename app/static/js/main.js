$(document).ready(function(){
  // var owl = $('.owl-carousel');
  // owl.owlCarousel({
    // items: 1,
    // loop: true,
    // margin: 10,
    // autoplay: true,
    // autoplayTimeout: 4000,
    // animateIn: true,
    // autoplayHoverPause: true
  // });
  $('.carousel').slick({
    slidesToShow: 1,
    // slidesToScroll: 3,
    autoplay: true,
    infinite: true,
    // autoplaySpeed: 2000,
    centerMode: true,
    centerPadding: '40px',
    variableWidth: true,
  });
});
