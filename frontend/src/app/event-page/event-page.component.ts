import { Component, OnInit } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {ActivatedRoute, Router} from "@angular/router";

@Component({
  selector: 'app-event-page',
  templateUrl: './event-page.component.html',
  styleUrls: ['./event-page.component.scss']
})
export class EventPageComponent implements OnInit {
  time = new Date().getTime();
  event: any;
  tweetListPage: Page<any>;
  isLoading = false;

  constructor(private http: HttpClient,
              private route: ActivatedRoute,
              private router: Router) { }

  ngOnInit() {
    this.http.get('/api/events/' + this.route.snapshot.params.id)
        .subscribe(event => {
          this.event = event;
          this.event.cluster_creating_time = new Date(this.event.cluster_creating_time);
        });

    this.route.queryParams.subscribe(params => {
      const page = params.page || 1;

      this.loadListOfTweets(page - 1);
    });
  }

  loadListOfTweets(page) {
    this.time = new Date().getTime();
    this.isLoading = true;

    this.http.get<Page<any>>('/api/events/' + this.route.snapshot.params.id + '/tweets?size=10&page=' + page)
        .subscribe(tweets => {
          this.tweetListPage = tweets;
          this.tweetListPage.content.forEach(tweet => {
            tweet.created_at = new Date(tweet.created_at);
          });

          this.isLoading = false;
        });
  }

  onPageSelected(page: number) {
    this.router.navigate([], {queryParams: {page: page}});
  }
}
