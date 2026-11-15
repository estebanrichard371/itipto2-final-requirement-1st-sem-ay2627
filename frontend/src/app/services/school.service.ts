
import {
  Injectable,
  signal,
  computed
} from '@angular/core';

import {
  HttpClient,
  HttpParams
} from '@angular/common/http';

import { tap } from 'rxjs/operators';


export interface Student {

  id: number;

  student_number: string;

  first_name: string;

  last_name: string;

  grade_section: string;

}


export interface Schedule {

  id: number;

  subject: string;

  start_time: string;

  end_time: string;

  room: string;

  instructor: string;

  day_of_week: string;

}


export interface AttendanceRecord {

  id: number;

  student_id: number;

  student_number: string;

  student_name: string;

  attendance_date: string;

  status: 'Present' | 'Absent' | 'Late';

  marked_by: string;

}


@Injectable({
  providedIn: 'root'
})

export class SchoolService {

  private baseUrl = 'http://127.0.0.1:8000';

  students = signal<Student[]>([]);

  schedules = signal<Schedule[]>([]);

  records = signal<AttendanceRecord[]>([]);

  dashboard = signal<any>({

    total_students: 0,

    present: 0,

    absent: 0,

    late: 0,

    attendance_percentage: 0

  });


  presentCount = computed(() =>
    this.records().filter(r => r.status === 'Present').length
  );

  absentCount = computed(() =>
    this.records().filter(r => r.status === 'Absent').length
  );

  lateCount = computed(() =>
    this.records().filter(r => r.status === 'Late').length
  );


  constructor(private http: HttpClient) {}


  // STUDENTS CRUD

  loadStudents() {

    return this.http.get<Student[]>(
      `${this.baseUrl}/students`
    ).pipe(

      tap(data => this.students.set(data))

    );

  }


  addStudent(data: Omit<Student, 'id'>) {

    return this.http.post(
      `${this.baseUrl}/students`,
      data
    ).pipe(

      tap(() => this.loadStudents().subscribe())

    );

  }


  updateStudent(
    id: number,
    data: Omit<Student, 'id'>
  ) {

    return this.http.put(
      `${this.baseUrl}/students/${id}`,
      data
    ).pipe(

      tap(() => this.loadStudents().subscribe())

    );

  }


  deleteStudent(id: number) {

    return this.http.delete(
      `${this.baseUrl}/students/${id}`
    ).pipe(

      tap(() => this.loadStudents().subscribe())

    );

  }


  // SCHEDULE CRUD

  loadSchedules() {

    return this.http.get<Schedule[]>(
      `${this.baseUrl}/schedules`
    ).pipe(

      tap(data => this.schedules.set(data))

    );

  }


  addSchedule(data: Omit<Schedule, 'id'>) {

    return this.http.post(
      `${this.baseUrl}/schedules`,
      data
    ).pipe(

      tap(() => this.loadSchedules().subscribe())

    );

  }


  updateSchedule(
    id: number,
    data: Omit<Schedule, 'id'>
  ) {

    return this.http.put(
      `${this.baseUrl}/schedules/${id}`,
      data
    ).pipe(

      tap(() => this.loadSchedules().subscribe())

    );

  }


  deleteSchedule(id: number) {

    return this.http.delete(
      `${this.baseUrl}/schedules/${id}`
    ).pipe(

      tap(() => this.loadSchedules().subscribe())

    );

  }


  // ATTENDANCE

  loadAttendance(attendanceDate?: string) {

    let params = new HttpParams();

    if (attendanceDate) {

      params = params.set(
        'attendance_date',
        attendanceDate
      );

    }

    return this.http.get<AttendanceRecord[]>(
      `${this.baseUrl}/attendance`,
      { params }
    ).pipe(

      tap(data => this.records.set(data))

    );

  }


  saveAttendance(data: {

    student_id: number;

    attendance_date: string;

    status: string;

  }) {

    return this.http.post(
      `${this.baseUrl}/attendance`,
      data
    );

  }


  updateAttendance(
    id: number,
    data: {
      student_id: number;
      attendance_date: string;
      status: string;
    }
  ) {

    return this.http.put(
      `${this.baseUrl}/attendance/${id}`,
      data
    ).pipe(

      tap(() => this.loadAttendance().subscribe())

    );

  }


  deleteAttendance(id: number) {

    return this.http.delete(
      `${this.baseUrl}/attendance/${id}`
    ).pipe(

      tap(() => this.loadAttendance().subscribe())

    );

  }


  // DASHBOARD

  loadDashboard(attendanceDate?: string) {

    let params = new HttpParams();

    if (attendanceDate) {

      params = params.set(
        'attendance_date',
        attendanceDate
      );

    }

    return this.http.get<any>(
      `${this.baseUrl}/dashboard`,
      { params }
    ).pipe(

      tap(data => this.dashboard.set(data))

    );

  }

}
