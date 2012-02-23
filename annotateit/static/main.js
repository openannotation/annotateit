jQuery(function ($) {
  function scrollTo(offset) {
    if (offset.top) {
      $('body').animate({
        scrollTop: offset.top - 10
      }, 300);
    }
  }

  $('nav').delegate('a', 'click', function (event) {
    var section = $(this.hash);

    if (section) {
      scrollTo(section.offset());
      event.preventDefault();      
    }
  });

  $('.js-relative-date').each(function () {
    m = moment($(this).attr('datetime'));
    $(this).text(m.fromNow());
  });

  $('.grabfocus').eq(0).focus();
});