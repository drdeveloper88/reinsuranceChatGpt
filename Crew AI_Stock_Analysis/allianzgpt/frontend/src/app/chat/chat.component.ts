import { Component, OnInit } from '@angular/core';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent implements OnInit {
  username = 'alice';
  password = 'Allianz123';
  token = '';
  queryText = '';
  chatLog: string[] = [];
  sources: any[] = []; 

  constructor(private api: ApiService) {}

  ngOnInit(): void {}

  login() {
    this.api.login(this.username, this.password).subscribe({
      next: (res: any) => {
        this.token = res?.access_token || '';
        this.chatLog.push('✅ Logged in successfully');
      },
      error: (err: any) => {
        this.chatLog.push('❌ Login failed ' + JSON.stringify(err));
      }
    });
  }

  sendQuery() {
    if (!this.token) {
      this.chatLog.push('⚠️ Authenticate first');
      return;
    }
    this.chatLog.push(`Q: ${this.queryText}`);

    // Streamed token-by-token UI experience
    const es = this.api.streamQuery(this.queryText, this.token);
    let partial = '';

    es.onmessage = (ev) => {
      if (!ev.data) return;
      if (ev.data === 'done') {
        this.chatLog.push('A: ' + partial);
        partial = '';
        es.close();
        return;
      }
      partial += ev.data;
      this.chatLog[this.chatLog.length - 1] = 'A: ' + partial;
    };

    es.onerror = () => {
      this.chatLog.push('❌ Stream closed or network error');
      es.close();
    };

    this.queryText = '';
  }
}
