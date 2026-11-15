import { Component, OnInit } from '@angular/core';

import { CommonModule } from '@angular/common';

import { Router, RouterLink } from '@angular/router';

import {

  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonCard,
  IonCardContent,
  IonGrid,
  IonRow,
  IonCol,
  IonIcon,
  IonButton,
  IonProgressBar,
  IonButtons

} from '@ionic/angular';


import { AuthService } from '../../services/auth.service';

import { SchoolService } from '../../services/school.service';


@Component({
  templateUrl: './dashboard.page.html',
  styleUrls: ['./dashboard.page.scss'],
  standalone: true,

  imports: [

    CommonModule,
    RouterLink,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonContent,
    IonCard,
    IonCardContent,
    IonGrid,
    IonRow,
    IonCol,
    IonIcon,
    IonButton,
    IonProgressBar,
    IonButtons

  ]



  
})


export class DashboardPage implements OnInit {

  today = new Date();


  constructor(

    public auth: AuthService,

    public school: SchoolService,

    private router: Router

  ) {}


  ngOnInit() {

    this.school.loadDashboard().subscribe({

      error: err => console.error(err)

    });

  }


  logout() {

    this.auth.logout();

    this.router.navigateByUrl('/login');

  }

}
