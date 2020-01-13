import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import {IkbPageComponent} from "./ikb-page/ikb-page.component";
import {EventListPageComponent} from "./event-list-page/event-list-page.component";
import {EventPageComponent} from "./event-page/event-page.component";
import {SlangViewPageComponent} from "./slang-view-page/slang-view-page.component";


const routes: Routes = [
  {path: 'ikb', component: IkbPageComponent},
  {path: 'ikb/:id', component: SlangViewPageComponent},
  {path: 'events', component: EventListPageComponent},
  {path: 'events/:id', component: EventPageComponent},
  {path: '', redirectTo: 'ikb', pathMatch: 'full'}

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
