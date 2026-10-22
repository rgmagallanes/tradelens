// READ-ONLY calculation helper. No OrderSend, CTrade, positions or order management.
#property strict
input string ExportSymbol="BTCUSDm";
int OnInit(){if(!SymbolSelect(ExportSymbol,true))return INIT_FAILED;EventSetTimer(2);return INIT_SUCCEEDED;}
void OnDeinit(const int reason){EventKillTimer();}
void OnTimer(){
 MqlTick t;
 if(!SymbolInfoTick(ExportSymbol,t))return;
 double buy=0,sell=0;
 bool ok=OrderCalcMargin(ORDER_TYPE_BUY,ExportSymbol,1.0,t.ask,buy) && OrderCalcMargin(ORDER_TYPE_SELL,ExportSymbol,1.0,t.bid,sell);
 if(!ok || buy<=0 || sell<=0)return;
 int f=FileOpen("btc-studio-margin.json",FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON|FILE_SHARE_READ);
 if(f==INVALID_HANDLE)return;
 string s=StringFormat("{\"version\":1,\"timestamp\":%I64d,\"symbol\":\"%s\",\"demo\":%s,\"terminal_connected\":%s,\"currency\":\"%s\",\"bid\":%.8f,\"ask\":%.8f,\"margin_buy_per_lot\":%.8f,\"margin_sell_per_lot\":%.8f}",(long)TimeGMT(),ExportSymbol,AccountInfoInteger(ACCOUNT_TRADE_MODE)==ACCOUNT_TRADE_MODE_DEMO?"true":"false",TerminalInfoInteger(TERMINAL_CONNECTED)?"true":"false",AccountInfoString(ACCOUNT_CURRENCY),t.bid,t.ask,buy,sell);
 FileWriteString(f,s);FileClose(f);
}
