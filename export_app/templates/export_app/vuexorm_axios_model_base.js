/* eslint-disable */
import Model from '@/models/Base';

export default class {{application_name|title}}{{model_name|title}}Base extends Model {
  static entity = '{{endpoint}}';

  static fields() {
    return {
      id: this.attr(null),
      {% for field in fields %}
      {{field.name}}: this.{% if field.type %}{{field.type}}{% else %}attr{% endif %}(),
      {% endfor %}
    };
  }
}
