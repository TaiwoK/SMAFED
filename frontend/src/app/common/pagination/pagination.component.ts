import {Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges} from '@angular/core';

@Component({
  selector: 'app-pagination',
  templateUrl: './pagination.component.html'
})
export class PaginationComponent implements OnInit, OnChanges {
  @Input()
  page: Page<any>;

  @Output()
  pageSelected: EventEmitter<number> = new EventEmitter();

  availablePages: number[];

  constructor() { }

  ngOnInit() {
    this.availablePages = [];
    const lastPageNumber = this.page.totalPages - 1;
    const startPage = Math.max(this.page.number - 3 - Math.max(0, this.page.number - lastPageNumber + 3), 0);
    const endPage = Math.min(this.page.number + 3 + Math.max(0, 3 - this.page.number), lastPageNumber);
    for (let i = startPage; i <= endPage; i++ ) {
      this.availablePages.push(i);
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes.page.isFirstChange()) { return; }
    this.ngOnInit();
  }

  prevPage() {
    if (this.page.first) { return; }
    this.selectPage(this.page.number - 1);
  }

  nextPage() {
    if (this.page.last) { return; }
    this.selectPage(this.page.number + 1);
  }

  selectPage(page: number) {
    if (this.page.number === page) { return; }
    this.pageSelected.emit(page + 1); // User friendly numbers, starts from 1 but not 0!
  }
}
