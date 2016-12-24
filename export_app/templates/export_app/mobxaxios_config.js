import axios from 'axios';     

const instance = axios.create({});

const xsrfConfig = {           
  xsrfCookieName: 'csrftoken', 
  xsrfHeaderName: 'X-CSRFToken',  
};  
      
instance.interceptors.request.use(config => ({...config, ...{url: `{{api_base}}/${config.url}/`}, ...xsrfConfig}));
        
instance.interceptors.response.use(response => {
  const errorMessage = response.data.errorMessage;
  return errorMessage ? Promise.reject(errorMessage) : response.data;
});       
              
export default instance;
