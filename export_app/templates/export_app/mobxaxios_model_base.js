import {{application_name}}{{model_name|title}}Store from '../../stores/{{application_name}}{{model_name}}';
import Model from './_base';   
import { observable } from 'mobx';
              
class {{application_name|title}}{{model_name|title}}Base extends Model {  
          
  store = {{application_name}}{{model_name|title}}Store;
              
  @observable id;
  {% for field in fields %}
    @observable {{field.name}}{% if field.has_default %} = {{field.default}}{% endif %};
  {% endfor %}
  {% for field in rels %}
    @observable {{field.name}}{% if field.has_default %} = {{field.default}}{% endif %};
  {% endfor %}
}

export default {{application_name|title}}{{model_name|title}}Base;

// vim: backupcopy=yes
