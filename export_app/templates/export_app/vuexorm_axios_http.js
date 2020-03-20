/* eslint-disable */
import config from '@/config';
import axios from 'axios';
import Vue from 'vue';

const Axios = axios.create({
  baseURL: config.api_base_url,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
  secure: false,
  withCredentials: false,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFTOKEN',
});
Vue.prototype.$http = Axios;
