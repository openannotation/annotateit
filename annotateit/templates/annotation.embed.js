{% from "_annotation.html" import render_annotation %}
(function () {
  'use strict';
  var scripts = document.getElementsByTagName('script'),
      self = scripts[scripts.length - 1],
      elem = $({{ render_annotation(annotation, user) | tojson }}).insertAfter(self),
      head = document.getElementsByTagName('head')[0],
      cssUrl = "{{ url_for('static', filename='annotation.embed.css', _external=True) }}";

  if (head !== undefined) {
    $('<link rel="stylesheet" href="' + cssUrl + '">').appendTo(head);
  } else {
    // We're almost certainly in an HTML5 document, so use scoped style
    $('<style scoped>@import url("' + cssUrl + '");</style>').appendTo(self);
  }
}());

