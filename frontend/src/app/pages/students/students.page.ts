
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
  IonSearchbar

} from '@ionic/angular';


import {
  SchoolService,
  Student
} from '../../services/school.service';


@Component({
  templateUrl: './students.page.html',
  styleUrls: ['./students.page.scss'],
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
    IonSearchbar

  ]

  

})


export class StudentsPage implements OnInit {

  form = {

    student_number: '',

    first_name: '',

    last_name: '',

    grade_section: ''

  };


  editingId: number | null = null;

  error = '';

  search = '';


  constructor(
    public school: SchoolService
  ) {}


  ngOnInit() {

    this.load();

  }


  load() {

    this.school.loadStudents().subscribe({

      error: (err: { error?: { detail?: string } }) => {

        this.error =
          err.error?.detail || 'Could not load students.';

      }

    });

  }


  filteredStudents() {

    const term = this.search.toLowerCase();

    return this.school.students().filter(
      (s: ReturnType<typeof this.school.students>[number]) =>

      `${s.first_name} ${s.last_name} ${s.student_number} ${s.grade_section}`
        .toLowerCase()
        .includes(term)

    );

  }


  save() {

    this.error = '';

    if (
      !this.form.student_number.trim() ||
      !this.form.first_name.trim() ||
      !this.form.last_name.trim()
    ) {

      this.error =
        'Student number, first name, and last name are required.';

      return;

    }


    const request = this.editingId

      ? this.school.updateStudent(
          this.editingId,
          this.form
        )

      : this.school.addStudent(this.form);


    request.subscribe({

      next: () => {

        this.reset();

      },

      error: (err: any) => {

        this.error =
          err.error?.detail || 'Could not save student.';

      }

    });

  }


  edit(student: Student) {

    this.editingId = student.id;

    this.form = {

      student_number: student.student_number,

      first_name: student.first_name,

      last_name: student.last_name,

      grade_section: student.grade_section || ''

    };

  }


  remove(id: number) {

    if (confirm('Archive this student?')) {

      this.school.deleteStudent(id).subscribe({

        error: (err: any) => {

          this.error =
            err.error?.detail || 'Could not delete student.';

        }

      });

    }

  }


  reset() {

    this.editingId = null;

    this.form = {

      student_number: '',

      first_name: '',

      last_name: '',

      grade_section: ''

    };

    this.error = '';

  }

}

