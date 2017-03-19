import { Injectable } from '@angular/core';
import { Http, Response, Headers } from '@angular/http';
import { Observable } from 'rxjs/Rx';
import {{application_name|title}}{{model_name|title}} from './{{model_name}}';

@Injectable()
export default class {{application_name|title}}{{model_name|title}}ServiceBase {
  private baseUrl: string = '{% url endpoint|add:'-list' %}';

  constructor(private http : Http){
  }

  query(search: any): Observable<{{application_name|title}}{{model_name|title}}[]> {
    const records$ = this.http
      .get(this.baseUrl, {search, headers: this.getHeaders()})
      .map(mapRecords)
      .catch(handleError);
    return records$;
  }

  getAll(): Observable<{{application_name|title}}{{model_name|title}}[]> {
    return this.query('');
  }

  get(id: string): Observable<{{application_name|title}}{{model_name|title}}> {
    const record$ = this.http
      .get(`${this.baseUrl}${id}/`, {headers: this.getHeaders()})
      .map(mapRecord)
      .catch(handleError);
    return record$;
  }

  create(record: {{application_name|title}}{{model_name|title}}) : Observable<{{application_name|title}}{{model_name|title}}>{
    const record$ = this.http
      .post(this.baseUrl, JSON.stringify(record), {headers: this.getHeaders()})
      .map(mapRecord)
      .catch(handleError);
    return record$;
  }

  update(record: {{application_name|title}}{{model_name|title}}) : Observable<{{application_name|title}}{{model_name|title}}>{
    const record$ = this.http
      .put(`${this.baseUrl}${record.id}/`, JSON.stringify(record), {headers: this.getHeaders()})
      .map(mapRecord)
      .catch(handleError);
    return record$;
  }

  delete(record: {{application_name|title}}{{model_name|title}}) : Observable<Response>{
    return this.http
      .delete(`${this.baseUrl}${record.id}/`, {headers: this.getHeaders()});
  }

  private getHeaders() {
    const headers = new Headers();
    headers.append('Accept', 'application/json');
    headers.append('content-type', 'application/json');
    return headers;
  }
}

function mapRecords(response:Response): {{application_name|title}}{{model_name|title}}[] {
  return response.json().results.map((json:any): {{application_name|title}}{{model_name|title}} => {
    return new {{application_name|title}}{{model_name|title}}(json);
  });
}

function mapRecord(response:Response): {{application_name|title}}{{model_name|title}} {
  return new {{application_name|title}}{{model_name|title}}(response.json());
}

function handleError(error: any) {
  console.error(error);
  return Observable.throw(error.message || 'Error while fetching {{application_name}}/{{model_name}}');
}
