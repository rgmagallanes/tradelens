// Read-only one-shot historical research exporter. No order/network APIs.
#property strict
#property indicator_chart_window
#property indicator_plots 0
input string ExportSymbol="BTCUSDm";
input datetime FromDate=D'2026.08.17 00:00';
int OnInit(){if(!SymbolSelect(ExportSymbol,true))return INIT_FAILED;EventSetTimer(10);return INIT_SUCCEEDED;}
void OnDeinit(const int reason){EventKillTimer();Comment("");}
int OnCalculate(const int rates_total,const int prev_calculated,const int begin,const double &price[]){return rates_total;}
int Load(ENUM_TIMEFRAMES tf,MqlRates &r[]){ResetLastError();return CopyRates(ExportSymbol,tf,FromDate,TimeTradeServer(),r);}
bool Ready(MqlRates &r[],int n,ENUM_TIMEFRAMES tf){return n>3&&r[0].time<=FromDate+PeriodSeconds(tf)*4;}
void WriteBars(int f,MqlRates &r[],int n){
 FileWriteString(f,"[");
 for(int i=0;i<n;i++){
  if(i>0)FileWriteString(f,",");
  string row=StringFormat("{\"time\":%I64d,\"open\":%.8f,\"high\":%.8f,\"low\":%.8f,\"close\":%.8f,\"closed\":%s}",(long)r[i].time,r[i].open,r[i].high,r[i].low,r[i].close,i<n-1?"true":"false");
  FileWriteString(f,row);
 }
 FileWriteString(f,"]");
}
void OnTimer(){
 if(AccountInfoInteger(ACCOUNT_TRADE_MODE)!=ACCOUNT_TRADE_MODE_DEMO){Comment("BTC Studio 2 Months: DEMO account required");return;}
 long needed=(long)((TimeTradeServer()-FromDate)/60)+1;
 long maxbars=TerminalInfoInteger(TERMINAL_MAXBARS);
 if(maxbars<needed){Comment(StringFormat("BTC Studio 2 Months: Max bars in chart is %I64d; set Tools > Options > Charts > Max bars in chart to 200000, restart MT5 and reattach this indicator.",maxbars));return;}
 MqlRates m1[],m5[],m15[],h1[];
 int n1=Load(PERIOD_M1,m1),n5=Load(PERIOD_M5,m5),n15=Load(PERIOD_M15,m15),nh=Load(PERIOD_H1,h1);
 Comment(StringFormat("BTC Studio 2 Months: downloading M1=%d M5=%d M15=%d H1=%d; waiting for August 17 coverage...",n1,n5,n15,nh));
 if(!Ready(m1,n1,PERIOD_M1)||!Ready(m5,n5,PERIOD_M5)||!Ready(m15,n15,PERIOD_M15)||!Ready(h1,nh,PERIOD_H1))return;
 int f=FileOpen("btc-studio-history-2months.json",FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON|FILE_SHARE_READ);
 if(f==INVALID_HANDLE){Comment("BTC Studio 2 Months: file write failed");return;}
 FileWriteString(f,StringFormat("{\"version\":1,\"timestamp\":%I64d,\"symbol\":\"%s\",\"terminal_connected\":%s,\"demo\":true,\"clock\":\"broker-server\",\"server_utc_offset_seconds\":%I64d,\"terminal_maxbars\":%I64d,\"requested_from\":%I64d,\"candles\":{\"M1\":",(long)TimeGMT(),ExportSymbol,TerminalInfoInteger(TERMINAL_CONNECTED)?"true":"false",(long)(TimeTradeServer()-TimeGMT()),maxbars,(long)FromDate));
 WriteBars(f,m1,n1);FileWriteString(f,",\"M5\":");WriteBars(f,m5,n5);FileWriteString(f,",\"M15\":");WriteBars(f,m15,n15);FileWriteString(f,",\"H1\":");WriteBars(f,h1,nh);FileWriteString(f,"}}");FileClose(f);
 Comment(StringFormat("BTC Studio 2 Months: EXPORT COMPLETE | M1 %d | M5 %d | M15 %d | H1 %d",n1,n5,n15,nh));EventKillTimer();
}
