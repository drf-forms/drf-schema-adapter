export default class {{application_name|title}}{{model_name|title}}Base {
  id:string;
  {% for field in fields %}
    {{field.name}}{% if field.type %}:{{field.type}}{% endif %};
  {% endfor %}
  {% for field in rels %}
    {{field.name}}:string{% if field.type == 'hasMany' %}[]{% endif %};
  {% endfor %}

  constructor(json:any) {
    if (json) {
      this.id = json.id;
      {% for field in fields %}
        this.{{field.name}} = json.{{field.name}};
      {% endfor %}
      {% for field in rels %}
        this.{{field.name}} = json.{{field.name}};
      {% endfor %}
    }
  }
}
