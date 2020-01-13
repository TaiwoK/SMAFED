import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { IkbPageComponent } from './ikb-page.component';

describe('IkbPageComponent', () => {
  let component: IkbPageComponent;
  let fixture: ComponentFixture<IkbPageComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ IkbPageComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(IkbPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
