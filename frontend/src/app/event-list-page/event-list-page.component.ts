import { Component, OnInit } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {ActivatedRoute, Router} from "@angular/router";

@Component({
  selector: 'app-event-list-page',
  templateUrl: './event-list-page.component.html',
  styleUrls: ['./event-list-page.component.scss']
})
export class EventListPageComponent implements OnInit {
  time = new Date().getTime();
  isLoading = false;
  eventListPage: Page<any>;

  constructor(private http: HttpClient,
              private router: Router,
              private route: ActivatedRoute) {
  }

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      const page = params.page || 1;

      this.loadListOfEvents(page - 1);
    });
  }

  loadListOfEvents(page) {
    this.time = new Date().getTime();
    this.isLoading = true;

    this.http.get<Page<any>>('/api/events?size=10&page=' + page)
        .subscribe(events => {
          this.eventListPage = events;
          events.content.forEach(event => {
            event.tweets.forEach(tweet => {
              tweet.created_at = new Date(tweet.created_at);
            });
          });

          this.isLoading = false;
        });
  }

  onPageSelected(page: number) {
    this.router.navigate([], {queryParams: {page: page}});
  }
}
