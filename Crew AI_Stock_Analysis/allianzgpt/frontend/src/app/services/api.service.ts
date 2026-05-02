import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/login`, {username, password});
  }

  query(text: string, token: string): Observable<any> {
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    return this.http.post(`${this.baseUrl}/query`, { query: text }, { headers });
  }

  streamQuery(text: string, token: string): EventSource {
    const url = new URL(`${this.baseUrl}/query/stream`, window.location.origin);
    url.searchParams.set('q', text);
    const es = new EventSource(url.toString(), { withCredentials: true } as any);
    return es;
  }
}
