import axios from '../config/axios-config';
import { observable } from 'mobx';

export default class Store {
  @observable records = [];
  @observable schema = {};
  @observable ui = {}

  endpoint = '';
  result = null;
  searchParam = 'search';
  lastFetch = null;

  transform(record) {
    return record;
  }

  get(id) {
    return  new Promise((resolve, reject) => {
      axios.get(`${this.endpoint}/${id}`).then((record) => {
        resolve(this.transform(record));
      }, reject)
    });
  }

  save(record) {
    let cache = [];
    const rv = JSON.parse(JSON.stringify(record, (key, value) => {
      if (key === 'store') {
        return;
      }
      if (typeof value === 'object' && value !== null) {
        if (cache.indexOf(value) !== -1) {
          // Circular reference found, discard key
          return;
        }
        // Store value in our collection
        cache.push(value);
      }
      return value;
    }));
    cache = null;
    if (record.id) {
      return axios.put(`${this.endpoint}/${record.id}`, rv).then(() => {
        record.is_error = false;
      }).catch(()=> {
        record.is_error = true;
      });
    } else {
      return axios.post(this.endpoint, rv).then((r) => {
        record.id = r.id;
        record.is_error = false;
      }).catch(() => {
        record.is_error = true;
      });
    }
  }

  _remove(record) {
    this.records.replace(this.records.filter((r)=> {
      if (record.id !== r.id) {
        return true;
      } else if (!record.id) {
        return record !== r;
      }
      return false;
    }));
  }

  delete(record) {
    if (record.id) {
      return axios.delete(`${this.endpoint}/${record.id}`).then(() => {
        this._remove(record);
      }).catch(() => {
        record.is_error = true;
      });
    } else {
      this._remove(record);
    }
  }

  create(record) {
    if (record == undefined) {
      record = {}
    }
    record = this.transform(record)
    this.records.push(record);
    return record;
  }

  search(value) {
    const search = {};
    search[this.searchParam] = value;
    this.fetchAll(search);
  }

  fetchAll(params) {
    return axios.get(this.endpoint, {params}).then((records) => {
      if (this.result !== null) {
        records = records[this.result];
      }
      this.records.replace(records.map(this.transform));
    });
  }

  fetchMeta() {
    return axios.request({method: 'options', url: this.endpoint}).then((meta) => {
      this.schema = meta.schema;
      this.ui = meta.ui;
    });
  }
}

// vim: backupcopy=yes
