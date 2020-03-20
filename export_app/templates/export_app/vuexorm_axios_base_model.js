/* eslint-disable */
import { Model } from '@vuex-orm/core';

export default class BaseModel extends Model {
  static fetchAll() {
    return this.api().get(`${this.entity}/`, { dataKey: 'results' });
  }

  static fetch(id) {
    return this.api().get(`${this.entity}/${id}/`);
  }

  static filter(params) {
    return this.api().get(`${this.entity}/`, { params, dataKey: 'results' });
  }

  static deleteRecord(item) {
    return this.api().delete(`${this.entity}/${item.$id}/`).then(() => {
      this.delete(item.$id);
    });
  }

  static updateRecord(item) {
    return this.api().put(`${this.entity}/${item.id}/`, item.$toJson());
  }
}
