import { Component, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpParams } from '@angular/common/http';
import { RouterLink, RouterLinkActive } from '@angular/router';

import {
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonItem,
  IonLabel,
  IonSelect,
  IonSelectOption,
  IonButton,
  IonSpinner
} from '@ionic/angular';

interface AttendanceSummary {
  student_id: number;
  student_number: string;
  student_name: string;
  total_present: number;
  total_absent: number;
  total_late: number;
  total_recorded_days: number;
  attendance_percentage: number;
}

@Component({
  selector: 'app-grading',
  templateUrl: './grading.page.html',
  styleUrls: ['./grading.page.scss'],
  standalone: true,
  imports: [
    RouterLink, 
    RouterLinkActive,
    CommonModule,
    FormsModule,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonContent,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonItem,
    IonLabel,
    IonSelect,
    IonSelectOption,
    IonButton,
    IonSpinner
  ]
})
export class GradingPage {

  private apiUrl =
    'http://127.0.0.1:8000/attendance/quarterly-summary';

  selectedPeriod = '1st Grading';

  startDate = '';
  endDate = '';

  periods = [
    '1st Grading',
    '2nd Grading',
    '3rd Grading',
    '4th Grading'
  ];

  records = signal<AttendanceSummary[]>([]);
  loading = signal(false);
  errorMessage = signal('');
  hasSearched = signal(false);

  totalPresent = computed(() =>
    this.records().reduce(
      (total, student) => total + student.total_present, 0
    )
  );

  totalAbsent = computed(() =>
    this.records().reduce(
      (total, student) => total + student.total_absent, 0
    )
  );

  totalLate = computed(() =>
    this.records().reduce(
      (total, student) => total + student.total_late, 0
    )
  );

  totalRecordedDays = computed(() =>
    this.records().reduce(
      (total, student) => total + student.total_recorded_days, 0
    )
  );

  overallAttendancePercentage = computed(() => {
    const total = this.totalRecordedDays();

    if (total === 0) {
      return 0;
    }

    return Number(
      (
        (this.totalPresent() + this.totalLate()) / total * 100
      ).toFixed(2)
    );
  });

  constructor(private http: HttpClient) {}

  loadAttendance(): void {

    if (!this.startDate || !this.endDate) {
      this.errorMessage.set(
        'Please select the start date and end date.'
      );
      return;
    }

    if (this.startDate > this.endDate) {
      this.errorMessage.set(
        'Start date cannot be later than end date.'
      );
      return;
    }

    this.loading.set(true);
    this.errorMessage.set('');
    this.hasSearched.set(true);
    this.records.set([]);

    const params = new HttpParams()
      .set('start_date', this.startDate)
      .set('end_date', this.endDate);

    this.http.get<{
      records: AttendanceSummary[]
    }>(this.apiUrl, { params }).subscribe({

      next: (response) => {
        this.records.set(response.records || []);
        this.loading.set(false);
      },

      error: (error) => {
        console.error('Attendance loading error:', error);

        this.errorMessage.set(
          error.error?.detail ||
          'Unable to load attendance records. Check your server connection.'
        );

        this.loading.set(false);
      }

    });
  }

}
