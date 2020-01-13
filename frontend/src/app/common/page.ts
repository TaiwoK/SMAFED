interface Page<T> {
    content: T[];
    size: number;
    number: number;
    totalPages: number;
    total: number;
    first: boolean;
    last: boolean;
}
