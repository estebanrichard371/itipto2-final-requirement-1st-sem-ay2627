import { Component, signal } from '@angular/core';

import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';

import { FormsModule } from '@angular/forms';

import { Router } from '@angular/router';

import {

  IonContent,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonItem,
  IonLabel,
  IonInput,
  IonButton,
  IonIcon,
  IonSegment,
  IonSegmentButton

} from '@ionic/angular';

import { AuthService } from '../../services/auth.service';


@Component({
  templateUrl: './login.page.html',
  styleUrls: ['./login.page.scss'],
  standalone: true,

  imports: [

    CommonModule,
    FormsModule,
    IonContent,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonItem,
    IonLabel,
    IonInput,
    IonButton,
    IonIcon,
    IonSegment,
    IonSegmentButton

  ],

  

})


export class LoginPage {

  username = 'teacher';

  password = 'teacher123';

  roleChoice = 'teacher';

  error = signal('');

  loading = signal(false);


  constructor(

    private auth: AuthService,

    private router: Router

  ) {}


  login() {

    this.error.set('');

    this.loading.set(true);


    this.auth.login(
      this.username.trim(),
      this.password
    ).subscribe({

      next: (response: { user: { role: string } }) => {

        this.loading.set(false);

        if (response.user.role !== this.roleChoice) {

          this.auth.logout();

          this.error.set(
            'Please choose the correct account type.'
          );

          return;

        }

        this.router.navigateByUrl('/dashboard');

      },


      error: (err: HttpErrorResponse) => {

        this.loading.set(false);

        this.error.set(
          err.error?.detail ||
          'Unable to connect to the server.'
        );

      }

    });

  }

}
