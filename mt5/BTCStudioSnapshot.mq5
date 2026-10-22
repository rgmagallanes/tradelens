// Read-only: exports quotes and specifications. Never submits orders.
#property strict
input string ExportSymbol="BTCUSDm";
int OnInit(){SymbolSelect(ExportSymbol,true); EventSetTimer(2); return INIT_SUCCEEDED;}
void OnDeinit(const int reason){EventKillTimer();}
void OnTimer(){
 MqlTick t;
 if(!SymbolInfoTick(ExportSymbol,t)) return;
 int f=FileOpen("btc-studio-snapshot.json",FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
 if(f==INVALID_HANDLE) return;
 string s=StringFormat("{\"timestamp\":%I64d,\"symbol\":\"%s\",\"bid\":%.8f,\"ask\":%.8f,\"contract_size\":%.8f,\"volume_min\":%.8f,\"volume_step\":%.8f}",(long)TimeGMT(),ExportSymbol,t.bid,t.ask,SymbolInfoDouble(ExportSymbol,SYMBOL_TRADE_CONTRACT_SIZE),SymbolInfoDouble(ExportSymbol,SYMBOL_VOLUME_MIN),SymbolInfoDouble(ExportSymbol,SYMBOL_VOLUME_STEP));
 FileWriteString(f,s); FileClose(f);
}
