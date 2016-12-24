import Store from './_base';   
import {{application_name|title}}{{model_name|title}} from '../models/{{application_name}}{{model_name}}';
          
export class {{application_name|title}}{{model_name|title}}Store extends Store {
  endpoint = '{{endpoint}}';
  {% if pagination_container %}
    result = '{{pagination_container}}';
  {% endif %}
          
  transform(record) {
    return new {{application_name|title}}{{model_name|title}}(record);  
  }       
              
};      
            
export default new {{application_name|title}}{{model_name|title}}Store;

