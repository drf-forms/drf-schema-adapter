/* eslint-disable */
import Ember from 'ember';
{% for item in items %}
import {{item.1}} from '{{item.2}}';
{% endfor %}

export const metadata = new Ember.Object({{root_metadata|safe}});

export default new Ember.Object({
  {% for item in items %}
    '{{item.0}}': new Ember.Object({{item.1}}),
  {% endfor %}
});
