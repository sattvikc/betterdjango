{
  {% for namespace, namespace_list in entry.items %}
  {% if namespace_list.is_namespace__ %}
    '{{ namespace }}' : {% include "api/apidef.js" with entry=namespace_list %}
  {% elif namespace == 'is_namespace__' %}
  {% else %}
    '{{ namespace }}' : function(data, callback) { 
      var url = '/api/v{{ namespace_list.version }}/{{ namespace_list.namespace }}.{{ namespace_list.apiname }}/';
      {% if namespace_list.http_method == 'GET' %}
      jQuery.get(url, data, function(result) {
        callback(result);
      });
      {% else %}
      jQuery.post(url, data, function(result) {
        callback(result);
      });
      {% endif %}
    },{% endif %}
  {% endfor %}
},
