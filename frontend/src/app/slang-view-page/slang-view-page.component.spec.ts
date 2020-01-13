import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SlangViewPageComponent } from './slang-view-page.component';

describe('SlangViewPageComponent', () => {
  let component: SlangViewPageComponent;
  let fixture: ComponentFixture<SlangViewPageComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SlangViewPageComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SlangViewPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
