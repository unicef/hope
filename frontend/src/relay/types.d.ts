
export interface UseQueryResponce<T> {
    props : T,
    error: unknown,
    retry :()=>{}

}