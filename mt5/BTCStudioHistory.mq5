// Read-only historical research exporter. No order or network APIs.
#property strict
#property indicator_chart_window
#property indicator_plots 0
input string ExportSymbol="BTCUSDm";
int OnInit(){if(!SymbolSelect(ExportSymbol,true))return INIT_FAILED;EventSetTimer(10);return INIT_SUCCEEDED;}
void OnDeinit(const int reason){EventKillTimer();Comment("");}
int OnCalculate(const int rates_total,const int prev_calculated,const int begin,const double &price[]){return rates_total;}
string Bars(ENUM_TIMEFRAMES tf,int requested,int &got){
 MqlRates r[];got=CopyRates(ExportSymbol,tf,0,requested,r);
 string out="[";
 for(int i=0;i<got;i++){
  if(i>0)out+=",";
  out+=StringFormat("{\"time\":%I64d,\"open\":%.8f,\"high\":%.8f,\"low\":%.8f,\"close\":%.8f,\"closed\":%s}",(long)r[i].time,r[i].open,r[i].high,r[i].low,r[i].close,i<got-1?"true":"false");
 }
 return out+"]";
}
void OnTimer(){
 if(AccountInfoInteger(ACCOUNT_TRADE_MODE)!=ACCOUNT_TRADE_MODE_DEMO){Comment("BTC Studio History: demo account required");return;}
 int n5=0,n15=0,n60=0;
 string b5=Bars(PERIOD_M5,4000,n5),b15=Bars(PERIOD_M15,1400,n15),b60=Bars(PERIOD_H1,400,n60);
 if(n5<3||n15<3||n60<3){Comment("BTC Studio History: downloading history; retrying...");return;}
 int f=FileOpen("btc-studio-history.json",FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON|FILE_SHARE_READ);
 if(f==INVALID_HANDLE){Comment("BTC Studio History: cannot write export");return;}
 string out=StringFormat("{\"version\":1,\"timestamp\":%I64d,\"symbol\":\"%s\",\"terminal_connected\":%s,\"demo\":true,\"clock\":\"broker-server\",\"candles\":{\"M1\":[],\"M5\":%s,\"M15\":%s,\"H1\":%s}}",(long)TimeGMT(),TerminalInfoInteger(TERMINAL_CONNECTED)?"true":"false",ExportSymbol,b5,b15,b60);
 // Symbol substituted separately to keep format argument order explicit.
 out=StringFormat("{\"version\":1,\"timestamp\":%I64d,\"symbol\":\"%s\",\"terminal_connected\":%s,\"demo\":true,\"clock\":\"broker-server\",\"candles\":{\"M1\":[],\"M5\":%s,\"M15\":%s,\"H1\":%s}}",(long)TimeGMT(),ExportSymbol,TerminalInfoInteger(TERMINAL_CONNECTED)?"true":"false",b5,b15,b60);
 FileWriteString(f,out);FileClose(f);
 Comment(StringFormat("BTC Studio History exported: M5 %d/4000 | M15 %d/1400 | H1 %d/400",n5,n15,n60));
 if(n5>=4000&&n15>=1400&&n60>=400)EventKillTimer();
}
