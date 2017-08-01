define('{{ember_app}}/models/{{application_name}}/{{model_name}}',
    ['exports', 'ember-data/model', 'ember-data/attr'{%if rels|length > 0 %}, 'ember-data/relationships'{%endif%}],
    function (exports, _emberDataModel, _emberDataAttr{%if rels|length > 0%}, _emberDataRelationships{%endif%}) {
  exports['default'] = _emberDataModel['default'].extend({
    {%for field in fields%}
      {{field.name}}: (0, _emberDataAttr['default'])({%if field.type %}'{{field.type}}'{%endif%}),
    {%endfor%}
    {%for field in rels%}
      {{field.name}}: (0, _emberDataRelationships['{{field.type}}'])('{{field.app}}/{{field.related_model}}', {async: true, inverse: {%if field.inverse %}'{{field.inverse}}'{% else %}null{% endif %}}),
    {%endfor%}
  });
});

