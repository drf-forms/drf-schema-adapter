/* eslint-disable */
import VuexORM from '@vuex-orm/core';
import VuexORMAxios from '@vuex-orm/plugin-axios';
import VuexORMisDirtyPlugin from '@vuex-orm/plugin-change-flags';
import axios from '@/store/http';
{% for item in items %}
import {{item.0}} from '@/models/{{item.1}}';
{% endfor %}

VuexORM.use(VuexORMAxios, {
  axios,
});
VuexORM.use(VuexORMisDirtyPlugin);
const database = new VuexORM.Database();
{% for item in items %}
database.register({{item.0}});
{% endfor %}
// export Axios;
export default database;
