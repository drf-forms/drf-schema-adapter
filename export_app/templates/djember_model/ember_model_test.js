import { moduleForModel, test } from 'ember-qunit';

moduleForModel('{{application_name}}/{{model_name}}', 'Unit | Model | {{application_name}}/{{model_name}}', {
  // Specify the other units that are required for this test.
  needs: [{% if rels|length > 0 %}{% for field in rels %}'model:{{field.app}}/{{field.related_model}}', {%endfor %}{% endif %}]
});

test('it exists', function(assert) {
  let model = this.subject();
  // let store = this.store();
  assert.ok(!!model);
});

