import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full',
  },

  {
    path: 'login',
    loadComponent: () => import('./pages/login/login.page').then((m) => m.LoginPage),
  },

  {
    path: 'dashboard',
    loadComponent: () => import('./pages/dashboard/dashboard.page').then((m) => m.DashboardPage),
  },

  {
    path: 'students',
    loadComponent: () => import('./pages/students/students.page').then((m) => m.StudentsPage),
  },

  {
    path: 'schedule',
    loadComponent: () => import('./pages/schedule/schedule.page').then((m) => m.SchedulePage),
  },

  {
    path: 'attendance',
    loadComponent: () => import('./pages/attendance/attendance.page').then((m) => m.AttendancePage),
  },

  {
    path: 'records',
    loadComponent: () => import('./pages/records/records.page').then((m) => m.RecordsPage),
  },
  {
    path: 'grading',
    loadComponent: () => import('./pages/grading/grading.page').then((m) => m.GradingPage),
  },
  {
    path: '**',
    redirectTo: 'login',
  },
  
];
