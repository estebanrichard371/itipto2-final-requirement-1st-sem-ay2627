import { ComponentFixture, TestBed } from '@angular/core/testing';
import { GradingPage } from './grading.page';

describe('GradingPage', () => {
  let component: GradingPage;
  let fixture: ComponentFixture<GradingPage>;

  beforeEach(() => {
    fixture = TestBed.createComponent(GradingPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
