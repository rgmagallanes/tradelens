// Read-only demo journal exporter. No orders, credentials, DLLs or network calls.
#property strict
#property indicator_chart_window
#property indicator_plots 0
string EscapeJSON(string s){StringReplace(s,"\\","\\\\");StringReplace(s,"\"","\\\"");StringReplace(s,"\r"," ");StringReplace(s,"\n"," ");return s;}
void AddID(ulong &ids[],ulong id){if(id==0)return;for(int i=0;i<ArraySize(ids);i++)if(ids[i]==id)return;int n=ArraySize(ids);ArrayResize(ids,n+1);ids[n]=id;}
int OnInit(){if(AccountInfoInteger(ACCOUNT_TRADE_MODE)!=ACCOUNT_TRADE_MODE_DEMO){Print("JournalStudioTrades requires a demo account.");return INIT_FAILED;}EventSetTimer(3);return INIT_SUCCEEDED;}
void OnDeinit(const int reason){EventKillTimer();}
int OnCalculate(const int rates_total,const int prev_calculated,const int begin,const double &price[]){return rates_total;}
void OnTimer(){
 if(AccountInfoInteger(ACCOUNT_TRADE_MODE)!=ACCOUNT_TRADE_MODE_DEMO || !TerminalInfoInteger(TERMINAL_CONNECTED))return;
 datetime now=TimeTradeServer(),from=now-7*86400;long offset=(long)(TimeTradeServer()-TimeGMT());
 // Exness UTC+0 only. Round small terminal clock differences, never infer historical DST.
 offset=(long)MathRound((double)offset/3600.0)*3600;
 ulong ids[];string positions="[";int pc=0;bool hedging=AccountInfoInteger(ACCOUNT_MARGIN_MODE)==ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;
 for(int i=0;i<PositionsTotal();i++){
  ulong ticket=PositionGetTicket(i);if(ticket==0)return;
  ulong id=(ulong)PositionGetInteger(POSITION_IDENTIFIER);AddID(ids,id);
  if(pc++>0)positions+=",";
  positions+=StringFormat("{\"position_id\":\"%I64u\",\"volume\":%.8f,\"floating_pnl\":%.8f,\"stop\":%.8f,\"target\":%.8f}",id,PositionGetDouble(POSITION_VOLUME),PositionGetDouble(POSITION_PROFIT),PositionGetDouble(POSITION_SL),PositionGetDouble(POSITION_TP));
 }
 positions+="]";
 if(!HistorySelect(from,now))return;
 int excluded=0;
 for(int i=0;i<HistoryDealsTotal();i++){
  ulong ticket=HistoryDealGetTicket(i);if(ticket==0)return;
  long type=HistoryDealGetInteger(ticket,DEAL_TYPE);
  if(type==DEAL_TYPE_BUY||type==DEAL_TYPE_SELL)AddID(ids,(ulong)HistoryDealGetInteger(ticket,DEAL_POSITION_ID));else excluded++;
 }
 string deals="[";int dc=0;
 for(int p=0;p<ArraySize(ids);p++){
  // Full lifecycle includes entry fills before the seven-day exit window.
  if(!HistorySelectByPosition(ids[p]))return;
  for(int i=0;i<HistoryDealsTotal();i++){
   ulong ticket=HistoryDealGetTicket(i);if(ticket==0)return;
   long type=HistoryDealGetInteger(ticket,DEAL_TYPE);if(type!=DEAL_TYPE_BUY&&type!=DEAL_TYPE_SELL)continue;
   long kind=HistoryDealGetInteger(ticket,DEAL_ENTRY);
   string entry=kind==DEAL_ENTRY_IN?"in":kind==DEAL_ENTRY_OUT?"out":kind==DEAL_ENTRY_OUT_BY?"out_by":"inout";
   if(dc++>0)deals+=",";
   deals+=StringFormat("{\"ticket\":\"%I64u\",\"position_id\":\"%I64u\",\"time\":%.3f,\"symbol\":\"%s\",\"side\":\"%s\",\"entry\":\"%s\",\"price\":%.8f,\"volume\":%.8f,\"profit\":%.8f,\"commission\":%.8f,\"swap\":%.8f,\"fee\":%.8f,\"stop\":%.8f,\"target\":%.8f}",ticket,ids[p],(double)HistoryDealGetInteger(ticket,DEAL_TIME_MSC)/1000.0-offset,EscapeJSON(HistoryDealGetString(ticket,DEAL_SYMBOL)),type==DEAL_TYPE_BUY?"buy":"sell",entry,HistoryDealGetDouble(ticket,DEAL_PRICE),HistoryDealGetDouble(ticket,DEAL_VOLUME),HistoryDealGetDouble(ticket,DEAL_PROFIT),HistoryDealGetDouble(ticket,DEAL_COMMISSION),HistoryDealGetDouble(ticket,DEAL_SWAP),HistoryDealGetDouble(ticket,DEAL_FEE),HistoryDealGetDouble(ticket,DEAL_SL),HistoryDealGetDouble(ticket,DEAL_TP));
  }
 }
 deals+="]";
 string account=AccountInfoString(ACCOUNT_SERVER)+"#"+StringFormat("%I64d",AccountInfoInteger(ACCOUNT_LOGIN));
 string out=StringFormat("{\"version\":1,\"timestamp\":%I64d,\"history_from\":%I64d,\"demo\":true,\"hedging\":%s,\"currency\":\"%s\",\"account_balance\":%.8f,\"server_utc_offset_seconds\":%I64d,\"account_key\":\"%s\",\"excluded_adjustments\":%d,\"deals\":%s,\"positions\":%s}",(long)TimeGMT(),(long)from-offset,hedging?"true":"false",EscapeJSON(AccountInfoString(ACCOUNT_CURRENCY)),AccountInfoDouble(ACCOUNT_BALANCE),offset,EscapeJSON(account),excluded,deals,positions);
 int f=FileOpen("studio-trades.tmp",FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
 if(f==INVALID_HANDLE)return;
 FileWriteString(f,out);FileFlush(f);FileClose(f);
 if(!FileMove("studio-trades.tmp",FILE_COMMON,"studio-trades.json",FILE_COMMON|FILE_REWRITE))Print("Journal export rename failed: ",GetLastError());
}
