import { Component, OnInit } from '@angular/core';

import { CommonModule } from '@angular/common';

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
  AttendanceRecord
} from '../../services/school.service';


@Component({
  templateUrl: './records.page.html',
  styleUrls: ['./records.page.scss'],
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


export class RecordsPage implements OnInit {

  filterDate = '';

  editStatuses: Record<number, string> = {};


  constructor(

    public auth: AuthService,

    public school: SchoolService

  ) {}


  ngOnInit() {

    this.load();

  }


  load() {

    this.school.loadAttendance(
      this.filterDate || undefined
    ).subscribe({

      next: (rows: AttendanceRecord[]) => {

        rows.forEach(record => {

          this.editStatuses[record.id] =
            record.status;

        });

      },

      error: (err: { error?: { detail?: string } }) => {

        alert(
          err.error?.detail || 'Could not load records.'
        );

      }

    });

  }


  update(record: AttendanceRecord) {

    if (this.auth.role() !== 'teacher') {

      alert('Only teachers can edit attendance.');

      return;

    }


    this.school.updateAttendance(

      record.id,

      {

        student_id: record.student_id,

        attendance_date: record.attendance_date,

        status:
          this.editStatuses[record.id] || record.status

      }

    ).subscribe({

      next: () => {

        alert('Attendance record updated.');

        this.load();

      },

      error: (err: { error?: { detail?: string } }) => {

        alert(
          err.error?.detail || 'Update failed.'
        );

      }

    });

  }


  remove(id: number) {

    if (confirm('Delete this attendance record?')) {

      this.school.deleteAttendance(id).subscribe({

        next: () => {

          alert('Attendance record deleted.');

          this.load();

        },

        error: (err: { error?: { detail?: string } }) => {

          alert(
            err.error?.detail || 'Delete failed.'
          );

        }

      });

    }

  }

}

