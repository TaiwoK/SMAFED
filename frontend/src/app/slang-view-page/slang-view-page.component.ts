import { Component, OnInit } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {ActivatedRoute, Router} from "@angular/router";

@Component({
  selector: 'app-slang-view-page',
  templateUrl: './slang-view-page.component.html',
  styleUrls: ['./slang-view-page.component.scss']
})
export class SlangViewPageComponent implements OnInit {
  slang: any;

  constructor(private http: HttpClient,
              private router: Router,
              private route: ActivatedRoute) { }

  ngOnInit() {
    this.http.get('/api/used-slangs/' + this.route.snapshot.params.id)
        .subscribe(slang => this.slang = slang);
  }

}
