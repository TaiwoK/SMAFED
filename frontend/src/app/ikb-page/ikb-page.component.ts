import {Component, OnInit} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {ActivatedRoute, Router} from "@angular/router";

@Component({
    selector: 'app-ikb-page',
    templateUrl: './ikb-page.component.html',
    styleUrls: ['./ikb-page.component.scss']
})
export class IkbPageComponent implements OnInit {
    search: string;
    isLoading = false;
    slangListPage: Page<any>;
    pageParams: any = {};

    constructor(private http: HttpClient,
                private router: Router,
                private route: ActivatedRoute) {
    }

    ngOnInit() {
        this.route.queryParams.subscribe(params => {
            const page = params.page || 1;
            this.search = params.search;

            this.loadListOfSlangs(page - 1, this.search);
        });
    }

    loadListOfSlangs(page, search=undefined) {
        this.isLoading = true;
        let url = '/api/used-slangs?size=9&page=' + page;

        if (search) {
            url += '&search=' + search;
        }

        this.http.get<Page<any>>(url)
            .subscribe(slangs => {
                this.slangListPage = slangs;
                this.slangListPage.content.forEach(slang => {
                    if (slang.definition && slang.definition.length > 110) {
                        slang.short_definition = slang.definition.substring(0, 100) + '...';
                    } else {
                        slang.short_definition = slang.definition;
                    }
                });
                this.isLoading = false;
            });
    }

    onPageSelected(page: number) {
        this.pageParams.page = page;
        this.updatePage();
    }

    onSearchChanged(newSearchValue) {
        this.pageParams.search = newSearchValue;
        this.pageParams.page = 1;
        this.updatePage();
    }

    private updatePage() {
        this.router.navigate([], {queryParams: {page: this.pageParams.page, search: this.pageParams.search}});
    }
}
