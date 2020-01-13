import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { EventPageComponent } from './event-page/event-page.component';
import { EventListPageComponent } from './event-list-page/event-list-page.component';
import { IkbPageComponent } from './ikb-page/ikb-page.component';
import {HttpClientModule} from "@angular/common/http";
import { PaginationComponent } from './common/pagination/pagination.component';
import { SlangViewPageComponent } from './slang-view-page/slang-view-page.component';
import {FormsModule} from "@angular/forms";

@NgModule({
  declarations: [
    AppComponent,
    EventPageComponent,
    EventListPageComponent,
    IkbPageComponent,
    PaginationComponent,
    SlangViewPageComponent,
  ],
  imports: [
    FormsModule,
    BrowserModule,
    AppRoutingModule,
    HttpClientModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
