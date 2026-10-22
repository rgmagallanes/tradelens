import {QueryClient} from '@tanstack/react-query';
export function createAccountQueryClient(){
 return new QueryClient({defaultOptions:{queries:{retry:false,staleTime:10000,gcTime:300000,refetchOnWindowFocus:false},mutations:{retry:false}}});
}
export function releaseAccountQueryClient(client:QueryClient){
 void client.cancelQueries();
 client.clear();
}
