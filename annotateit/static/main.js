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

  $('.editable').on('click', function (event) {
    var key = $(this).data('key');

    if (typeof key === 'undefined' || key == null) {
      return;
    }

    var self = this;
    var form = '<form><input type=text name="' + key + '"></form>';
    var data = {};

    var $f = $(form);
    var $i = $f.find('input');

    var restore = function (val) { $(self).text(val).replaceAll($f); }

    $(this)
      .after($f)
      .detach()

    $i.val(this.innerText)
      .focus()
      .on('blur', function () { restore(self.innerText); })

    $f.on('submit', function (e) {
      e.preventDefault();
      data[key] = $i.val();
      $.post('', data)
        .done(restore)
        .fail(function(resp) {
          restore(self.innerText);
          alert("Error updating field:\n" + resp.responseText);
        });
    });
  });
});