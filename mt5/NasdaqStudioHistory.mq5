// Read-only one-shot historical research exporter. No order/network APIs.
#property strict
#property indicator_chart_window
#property indicator_plots 0
string ExportSymbol;
string EscapeJSON(string s){StringReplace(s,"\\","\\\\");StringReplace(s,"\"","\\\"");StringReplace(s,"\r"," ");StringReplace(s,"\n"," ");return s;}
input datetime FromDate=D'2026.08.17 00:00';
int OnInit(){ExportSymbol=_Symbol;string upper=ExportSymbol;StringToUpper(upper);if(StringFind(upper,"USTEC")<0&&StringFind(upper,"US100")<0){Print("NasdaqStudioHistory: attach only to your USTEC or US100 chart.");return INIT_FAILED;}if(AccountInfoInteger(ACCOUNT_TRADE_MODE)!=ACCOUNT_TRADE_MODE_DEMO)return INIT_FAILED;if(!SymbolSelect(ExportSymbol,true))return INIT_FAILED;EventSetTimer(10);return INIT_SUCCEEDED;}
void OnDeinit(const int reason){EventKillTimer();Comment("");}
int OnCalculate(const int rates_total,const int prev_calculated,const int begin,const double &price[]){return rates_total;}
int Load(ENUM_TIMEFRAMES tf,MqlRates &r[]){ResetLastError();return CopyRates(ExportSymbol,tf,FromDate,TimeTradeServer(),r);}
bool Ready(MqlRates &r[],int n,ENUM_TIMEFRAMES tf){return n>3&&r[0].time<=FromDate+86400;}
void WriteBars(int f,MqlRates &r[],int n){
 FileWriteString(f,"[");
 for(int i=0;i<n;i++){
  if(i>0)FileWriteString(f,",");
  string row=StringFormat("{\"time\":%I64d,\"open\":%.8f,\"high\":%.8f,\"low\":%.8f,\"close\":%.8f,\"tick_volume\":%I64d,\"real_volume\":%I64d,\"closed\":%s}",(long)r[i].time,r[i].open,r[i].high,r[i].low,r[i].close,(long)r[i].tick_volume,(long)r[i].real_volume,i<n-1?"true":"false");
  FileWriteString(f,row);
 }
 FileWriteString(f,"]");
}
void OnTimer(){
 if(!TerminalInfoInteger(TERMINAL_CONNECTED)){Comment("TradeLens Nasdaq History: MT5 disconnected; waiting.");return;}
 if(AccountInfoInteger(ACCOUNT_TRADE_MODE)!=ACCOUNT_TRADE_MODE_DEMO){Comment("TradeLens Nasdaq History: DEMO account required");return;}
 long needed=(long)((TimeTradeServer()-FromDate)/60)+1;
 long maxbars=TerminalInfoInteger(TERMINAL_MAXBARS);
 if(maxbars<needed){Comment(StringFormat("TradeLens Nasdaq History: Max bars in chart is %I64d; set Tools > Options > Charts > Max bars in chart to 200000, restart MT5 and reattach this indicator.",maxbars));return;}
 MqlRates m1[],m5[],m15[],h1[];
 int n1=Load(PERIOD_M1,m1),n5=Load(PERIOD_M5,m5),n15=Load(PERIOD_M15,m15),nh=Load(PERIOD_H1,h1);
 Comment(StringFormat("TradeLens Nasdaq History: downloading M1=%d M5=%d M15=%d H1=%d; waiting for August 17 coverage...",n1,n5,n15,nh));
 if(!Ready(m1,n1,PERIOD_M1)||!Ready(m5,n5,PERIOD_M5)||!Ready(m15,n15,PERIOD_M15)||!Ready(h1,nh,PERIOD_H1))return;
 int f=FileOpen("nasdaq-studio-history.tmp",FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
 if(f==INVALID_HANDLE){Comment("TradeLens Nasdaq History: file write failed");return;}
 FileWriteString(f,StringFormat("{\"version\":1,\"timestamp\":%I64d,\"symbol\":\"%s\",\"terminal_connected\":%s,\"demo\":true,\"clock\":\"broker-server\",\"server_utc_offset_seconds\":%I64d,\"terminal_maxbars\":%I64d,\"requested_from\":%I64d,\"candles\":{\"M1\":",(long)TimeGMT(),EscapeJSON(ExportSymbol),TerminalInfoInteger(TERMINAL_CONNECTED)?"true":"false",(long)MathRound((double)(TimeTradeServer()-TimeGMT())/3600.0)*3600,maxbars,(long)FromDate));
 WriteBars(f,m1,n1);FileWriteString(f,",\"M5\":");WriteBars(f,m5,n5);FileWriteString(f,",\"M15\":");WriteBars(f,m15,n15);FileWriteString(f,",\"H1\":");WriteBars(f,h1,nh);FileWriteString(f,"},\"specs\":");
 MqlTick tick;bool quoted=SymbolInfoTick(ExportSymbol,tick);
 FileWriteString(f,StringFormat("{\"tick_size\":%.8f,\"point\":%.8f,\"contract_size\":%.8f,\"tick_value_profit\":%.8f,\"tick_value_loss\":%.8f,\"volume_min\":%.8f,\"volume_step\":%.8f,\"profit_currency\":\"%s\",\"account_currency\":\"%s\",\"chart_mode\":%I64d,\"observed_bid\":%.8f,\"observed_ask\":%.8f,\"quote_time\":%I64d,\"commission_verified\":false,\"cost_note\":\"Current quote/specification only, not historical spreads or commissions\"}}",SymbolInfoDouble(ExportSymbol,SYMBOL_TRADE_TICK_SIZE),SymbolInfoDouble(ExportSymbol,SYMBOL_POINT),SymbolInfoDouble(ExportSymbol,SYMBOL_TRADE_CONTRACT_SIZE),SymbolInfoDouble(ExportSymbol,SYMBOL_TRADE_TICK_VALUE_PROFIT),SymbolInfoDouble(ExportSymbol,SYMBOL_TRADE_TICK_VALUE_LOSS),SymbolInfoDouble(ExportSymbol,SYMBOL_VOLUME_MIN),SymbolInfoDouble(ExportSymbol,SYMBOL_VOLUME_STEP),EscapeJSON(SymbolInfoString(ExportSymbol,SYMBOL_CURRENCY_PROFIT)),EscapeJSON(AccountInfoString(ACCOUNT_CURRENCY)),SymbolInfoInteger(ExportSymbol,SYMBOL_CHART_MODE),quoted?tick.bid:0,quoted?tick.ask:0,quoted?(long)tick.time:0));
 FileFlush(f);FileClose(f);
 if(!FileMove("nasdaq-studio-history.tmp",FILE_COMMON,"nasdaq-studio-history.json",FILE_COMMON|FILE_REWRITE)){Comment("TradeLens Nasdaq History: export rename failed; retrying.");return;}
 Comment(StringFormat("TradeLens Nasdaq History: EXPORT COMPLETE | M1 %d | M5 %d | M15 %d | H1 %d",n1,n5,n15,nh));EventKillTimer();
}
