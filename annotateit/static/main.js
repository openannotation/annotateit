jQuery(function ($) {
  function scrollTo(offset) {
    if (offset.top) {
      $('body').animate({
        scrollTop: offset.top - 10
      }, 300);
    }
  }

  $('nav').on('click', 'a', function (event) {
    var section = $(this.hash);

    if (section) {
      scrollTo(section.offset());
      event.preventDefault();      
    }
  });

  $('.js-relative-date').each(function () {
    var m = moment($(this).attr('datetime'));
    $(this).text(m.fromNow());
  });

  $('.grabfocus').eq(0).focus();

  function editableClick (event) {
    var key = $(this).data('key');

    if (typeof key === 'undefined' || key == null) {
      return;
    }

    var self = this;
    var text = $(this).text();
    var form = '<form class="inline-edit"><input type=text name="' + key + '"></form>';
    var data = {};

    var $f = $(form);
    var $i = $f.find('input');

    var restore = function (val) { 
      $(self)
        .text(val)
        .addClass('editable')
        .one('click', editableClick);
    };

    $(this)
      .html($f)
      .removeClass('editable');

    $i.val(text)
      .focus()
      .on('blur', function () { restore(text); });

    $f.on('submit', function (e) {
      e.preventDefault();
      data[key] = $i.val();
      $.post('', data)
        .done(restore)
        .fail(function(resp) {
          restore(text);
          alert("Error updating field:\n" + resp.responseText);
        });
    });
  }

  $('.editable').one('click', editableClick);
});