// Read-only indicator. No trading API, credentials, or network calls.
#property strict
#property indicator_chart_window
#property indicator_plots 0
input string ExportSymbol="XAUUSDm";
long last_tick_msc=0;
ulong last_change=0;
bool observed_change=false;
int OnInit(){
 if(!SymbolSelect(ExportSymbol,true)) return INIT_FAILED;
 EventSetTimer(2); return INIT_SUCCEEDED;
}
void OnDeinit(const int reason){EventKillTimer();}
int OnCalculate(const int rates_total,const int prev_calculated,const int begin,const double &price[]){return rates_total;}

string ExportBars(ENUM_TIMEFRAMES tf){
 MqlRates rates[];
 int count=CopyRates(ExportSymbol,tf,0,tf==PERIOD_D1?20:400,rates);
 string out="[";
 for(int i=0;i<count;i++){
  if(i>0) out+=",";
  out+=StringFormat("{\"time\":%I64d,\"open\":%.8f,\"high\":%.8f,\"low\":%.8f,\"close\":%.8f,\"tick_volume\":%I64d,\"real_volume\":%I64d,\"closed\":%s}",(long)rates[i].time,rates[i].open,rates[i].high,rates[i].low,rates[i].close,(long)rates[i].tick_volume,(long)rates[i].real_volume,i<count-1?"true":"false");
 }
 return out+"]";
}
void ExportHistory(bool connected,bool demo){
 string bars="{\"M1\":"+ExportBars(PERIOD_M1)+",\"M5\":"+ExportBars(PERIOD_M5)+",\"M15\":"+ExportBars(PERIOD_M15)+",\"H1\":"+ExportBars(PERIOD_H1)+",\"H4\":"+ExportBars(PERIOD_H4)+",\"D1\":"+ExportBars(PERIOD_D1)+"}";
 int f=FileOpen("xau-studio-candles.json",FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON|FILE_SHARE_READ);
 if(f==INVALID_HANDLE) return;
 string out=StringFormat("{\"version\":1,\"timestamp\":%I64d,\"symbol\":\"%s\",\"terminal_connected\":%s,\"demo\":%s,\"clock\":\"broker-server\",\"server_utc_offset_seconds\":%I64d,\"candles\":%s}",(long)TimeGMT(),ExportSymbol,connected?"true":"false",demo?"true":"false",(long)(TimeTradeServer()-TimeGMT()),bars);
 FileWriteString(f,out);FileClose(f);
}

void OnTimer(){
 MqlTick t;
 if(!SymbolInfoTick(ExportSymbol,t)) return;
 if(last_tick_msc!=0 && t.time_msc!=last_tick_msc){last_change=GetTickCount64();observed_change=true;}
 last_tick_msc=t.time_msc;
 double age=observed_change ? (double)(GetTickCount64()-last_change)/1000.0 : -1.0;
 bool connected=(bool)TerminalInfoInteger(TERMINAL_CONNECTED);
 bool demo=AccountInfoInteger(ACCOUNT_TRADE_MODE)==ACCOUNT_TRADE_MODE_DEMO;
 int f=FileOpen("xau-studio-quotes.json",FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON|FILE_SHARE_READ);
 if(f==INVALID_HANDLE) return;
 string s=StringFormat("{\"version\":1,\"timestamp\":%I64d,\"symbol\":\"%s\",\"bid\":%.8f,\"ask\":%.8f,\"contract_size\":%.8f,\"volume_min\":%.8f,\"volume_step\":%.8f,\"tick_time_msc\":%I64d,\"quote_age_seconds\":%.3f,\"terminal_connected\":%s,\"demo\":%s}",(long)TimeGMT(),ExportSymbol,t.bid,t.ask,SymbolInfoDouble(ExportSymbol,SYMBOL_TRADE_CONTRACT_SIZE),SymbolInfoDouble(ExportSymbol,SYMBOL_VOLUME_MIN),SymbolInfoDouble(ExportSymbol,SYMBOL_VOLUME_STEP),t.time_msc,age,connected?"true":"false",demo?"true":"false");
 double mb=0,ms=0;
 // Margin comes from the separate read-only BTCStudioMargin (BTC only; not used for Gold) helper.
 string basis=SymbolInfoInteger(ExportSymbol,SYMBOL_CHART_MODE)==SYMBOL_CHART_MODE_BID?"bid":"last";
 s=StringSubstr(s,0,StringLen(s)-1)+StringFormat(",\"chart_basis\":\"%s\",\"tick_size\":%.8f,\"volume_max\":%.8f,\"currency\":\"%s\",\"margin_buy_per_lot\":%.8f,\"margin_sell_per_lot\":%.8f}",basis,SymbolInfoDouble(ExportSymbol,SYMBOL_TRADE_TICK_SIZE),SymbolInfoDouble(ExportSymbol,SYMBOL_VOLUME_MAX),AccountInfoString(ACCOUNT_CURRENCY),mb,ms);
 FileWriteString(f,s);FileClose(f);
 ExportHistory(connected,demo);
}
