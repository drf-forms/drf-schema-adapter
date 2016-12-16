define([
  'angular',
  'angular-resource'           
], function (angular) {        
  angular.module('app.resources.{{application_name}}-{{model_name}}', [
    'ngResource'
  ])    
  .service('{{model_name|title}}', function ($resource) {
    return $resource('{{api_base}}/{{endpoint}}/:id', { id: '@id' })
  })
});
