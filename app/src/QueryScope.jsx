import {useEffect,useState} from 'react';
import {QueryClientProvider} from '@tanstack/react-query';
import {createAccountQueryClient,releaseAccountQueryClient} from './queryClient.ts';
// A new provider is mounted for each hosted identity. No financial data is persisted.
export default function QueryScope({children}){
 const [client]=useState(createAccountQueryClient);
 useEffect(()=>()=>releaseAccountQueryClient(client),[client]);
 return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
