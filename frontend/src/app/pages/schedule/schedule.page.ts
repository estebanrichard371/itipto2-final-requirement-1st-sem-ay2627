
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import {
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonCard,
  IonCardContent,
  IonItem,
  IonLabel,
  IonInput,
  IonButton,
  IonIcon,
  IonSelect,
  IonSelectOption

} from '@ionic/angular';


import { AuthService } from '../../services/auth.service';

import {
  SchoolService,
  Schedule
} from '../../services/school.service';


@Component({
  templateUrl: './schedule.page.html',
  styleUrls: ['./schedule.page.scss'],
  standalone: true,

  imports: [

    CommonModule,
    FormsModule,
    RouterLink,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonContent,
    IonCard,
    IonCardContent,
    IonItem,
    IonLabel,
    IonInput,
    IonButton,
    IonIcon,
    IonSelect,
    IonSelectOption

  ],

  

})


export class SchedulePage implements OnInit {

  days = [

    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday'

  ];


  form = {

    subject: '',

    start_time: '',

    end_time: '',

    room: '',

    instructor: '',

    day_of_week: 'Monday'

  };


  editingId: number | null = null;

  error = '';


  constructor(

    public auth: AuthService,

    public school: SchoolService

  ) {}


  ngOnInit() {

    this.school.loadSchedules().subscribe({

      error: (err: { error?: { detail?: string } }) => {

        this.error =
          err.error?.detail || 'Could not load schedules.';

      }

    });

  }


  save() {

    if (
      !this.form.subject.trim() ||
      !this.form.start_time.trim() ||
      !this.form.end_time.trim()
    ) {

      this.error =
        'Subject, start time, and end time are required.';

      return;

    }


    const request = this.editingId

      ? this.school.updateSchedule(
          this.editingId,
          this.form
        )

      : this.school.addSchedule(this.form);


    request.subscribe({

      next: () => this.reset(),

      error: (err: HttpErrorResponse) => {

        this.error =
          err.error?.detail || 'Could not save schedule.';

      }

    });

  }


  edit(s: Schedule) {

    this.editingId = s.id;

    this.form = {

      subject: s.subject,

      start_time: s.start_time,

      end_time: s.end_time,

      room: s.room,

      instructor: s.instructor,

      day_of_week: s.day_of_week

    };

  }


  remove(id: number) {

    if (confirm('Delete this schedule?')) {

      this.school.deleteSchedule(id).subscribe({

        error: (err: HttpErrorResponse) => {

          this.error =
            err.error?.detail || 'Could not delete schedule.';

        }

      });

    }

  }


  reset() {

    this.editingId = null;

    this.form = {

      subject: '',

      start_time: '',

      end_time: '',

      room: '',

      instructor: '',

      day_of_week: 'Monday'

    };

    this.error = '';

  }

}

