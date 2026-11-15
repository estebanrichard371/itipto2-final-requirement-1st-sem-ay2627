
import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs/operators';

export interface AppUser {
  id: number;
  username: string;
  full_name: string;
  role: 'registrar' | 'teacher';
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private baseUrl = 'http://127.0.0.1:8000';

  user = signal<AppUser | null>(
    this.readSavedUser()
  );

  constructor(private http: HttpClient) {}

  private readSavedUser(): AppUser | null {
    try {
      return JSON.parse(
        localStorage.getItem('attendance_user') || 'null'
      );
    } catch {
      return null;
    }
  }

  login(username: string, password: string) {

    return this.http.post<any>(
      `${this.baseUrl}/auth/login`,
      { username, password }
    ).pipe(

      tap(response => {

        localStorage.setItem(
          'attendance_token',
          response.access_token
        );

        localStorage.setItem(
          'attendance_user',
          JSON.stringify(response.user)
        );

        this.user.set(response.user);

      })

    );

  }

  logout() {

    localStorage.removeItem('attendance_token');

    localStorage.removeItem('attendance_user');

    this.user.set(null);

  }

  isLoggedIn(): boolean {

    return !!localStorage.getItem('attendance_token')
      && !!this.user();

  }

  role(): string {

    return this.user()?.role || '';

  }

}
