(function (window, document) {
  window._annotatorConfig = {
    "auth": { "tokenUrl": "{{ root }}/api/token" },
    "store": { "prefix": "{{ root }}/api" },
    "tags": true
  };
  s = document.body.appendChild(document.createElement('script'));
  s.language = 'javascript';
  s.src = 'http://assets.annotateit.org/bookmarklet/bootstrap.js';
})(this, this.document);
