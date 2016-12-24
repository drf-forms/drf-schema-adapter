import { observable } from 'mobx';
   
class Model {
          
  store = null;
   
  @observable is_error = false;
              
  constructor(params) {
    this.init(params);
  }           
              
  init(params) {
    for (let field in params) {
      this[field] = params[field];    
    }   
  }  
        
  save() {
    return this.store.save(this);   
  }         
        
  reload() {
    return this.store.get(this.id).then((params) => {
      this.init(params);
    });     
  }         
   
  delete() {
    return this.store.delete(this); 
  }       
              
}           
            
export default Model;
