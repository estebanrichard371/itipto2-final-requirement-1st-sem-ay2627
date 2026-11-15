
import { bootstrapApplication } from '@angular/platform-browser';

import {
  provideIonicAngular
} from '@ionic/angular';

import {
  provideRouter
} from '@angular/router';

import {
  provideHttpClient,
  withInterceptors
} from '@angular/common/http';

import { addIcons } from 'ionicons';

import {

  school,
  home,
  calendar,
  checkmarkCircle,
  list,
  logIn,
  logOut,
  people,
  create,
  trash,
  save,
  eye,
  time,
  location,
  person,
  refresh,
  closeCircle,
  add

} from 'ionicons/icons';


import { AppComponent } from './app/app.component';

import { routes } from './app/app.routes';

import {
  authInterceptor
} from './app/services/auth.interceptor';


addIcons({

  school,
  home,
  calendar,
  checkmarkCircle,
  list,
  logIn,
  logOut,
  people,
  create,
  trash,
  save,
  eye,
  time,
  location,
  person,
  refresh,
  closeCircle,
  add

});


bootstrapApplication(AppComponent, {

  providers: [

    provideIonicAngular(),

    provideRouter(routes),

    provideHttpClient(
      withInterceptors([authInterceptor])
    )

  ]

}).catch(err => console.error(err));
