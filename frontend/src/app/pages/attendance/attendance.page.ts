import { Component, OnInit, signal } from '@angular/core';

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
  IonSelect,
  IonSelectOption,
  IonButton,
  IonIcon,
  IonInput

} from '@ionic/angular';


import { SchoolService } from '../../services/school.service';


@Component({

  standalone: true,
  templateUrl: './attendance.page.html',
  styleUrls: ['./attendance.page.scss'],
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
    IonSelect,
    IonSelectOption,
    IonButton,
    IonIcon,
    IonInput

  ],



})


export class AttendancePage implements OnInit {

  attendanceDate = new Date()
    .toISOString()
    .slice(0, 10);


  statuses: Record<number, string> = {};


  message = signal('');

  saving = signal(false);


  constructor(
    public school: SchoolService
  ) {}


  ngOnInit() {

    this.school.loadStudents().subscribe({

      next: () => {

        this.school.students().forEach((student: { id: number }) => {

          this.statuses[student.id] = 'Present';

        });

        this.loadExisting();

      },

      error: (err: any) => {

        this.message.set(
          err.error?.detail || 'Could not load students.'
        );

      }

    });

  }


  loadExisting() {

    this.school.loadAttendance(
      this.attendanceDate
    ).subscribe({

      next: (records: { student_id: number; status: string }[]) => {

        records.forEach(record => {

          this.statuses[record.student_id] =
            record.status;

        });

      },

      error: (err: any) => {

        this.message.set(
          err.error?.detail || 'Could not load attendance.'
        );

      }

    });

  }


  async save() {

    const students = this.school.students();

    if (!students.length) {

      this.message.set('No students found.');

      return;

    }


    this.saving.set(true);

    this.message.set('');

    let failed = false;


    for (const student of students) {

      try {

        await new Promise<void>((resolve, reject) => {

          this.school.saveAttendance({

            student_id: student.id,

            attendance_date: this.attendanceDate,

            status: this.statuses[student.id] || 'Present'

          }).subscribe({

            next: () => resolve(),

            error: (err: any) => reject(err)

          });

        });

      } catch (err: any) {

        failed = true;

        this.message.set(
          err.error?.detail ||
          'Some attendance entries could not be saved.'
        );

        break;

      }

    }


    this.saving.set(false);


    if (!failed) {

      this.message.set(
        'Attendance saved successfully!'
      );

      this.school.loadAttendance(
        this.attendanceDate
      ).subscribe();

      this.school.loadDashboard(
        this.attendanceDate
      ).subscribe();

    }

  }


  reset() {

    this.school.students().forEach((student: { id: number }) => {

      this.statuses[student.id] = 'Present';

    });

    this.message.set(
      'All statuses reset to Present. Press Save Attendance to apply.'
    );

  }

}

