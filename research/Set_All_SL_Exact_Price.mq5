//+------------------------------------------------------------------+
//| Set_All_SL_Exact_Price.mq5                                       |
//| Applies one exact SL price to open positions on the chart symbol. |
//+------------------------------------------------------------------+
#property strict
#property script_show_inputs
#include <Trade/Trade.mqh>

input double StopLossPrice = 42500.0;  // Exact SL price (NOT points)
input bool   CurrentChartSymbolOnly = true; // false = all account symbols
input bool   IncludeBuyPositions = true;
input bool   IncludeSellPositions = true;

CTrade trade;

void OnStart()
{
   if(StopLossPrice <= 0.0 || !MathIsValidNumber(StopLossPrice))
   {
      Alert("Invalid StopLossPrice. Enter a positive market price.");
      return;
   }

   int updated = 0, skipped = 0, failed = 0;
   for(int i = PositionsTotal() - 1; i >= 0; --i)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
      {
         failed++;
         continue;
      }

      string symbol = PositionGetString(POSITION_SYMBOL);
      if(CurrentChartSymbolOnly && symbol != _Symbol) continue;

      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      if((type == POSITION_TYPE_BUY && !IncludeBuyPositions) ||
         (type == POSITION_TYPE_SELL && !IncludeSellPositions)) continue;

      double tp = PositionGetDouble(POSITION_TP);
      double currentSL = PositionGetDouble(POSITION_SL);
      double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
      double tickSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
      int digits = (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS);
      if(point <= 0 || tickSize <= 0) { failed++; continue; }

      double sl = NormalizeDouble(MathRound(StopLossPrice / tickSize) * tickSize, digits);
      // Avoid unintended SL price changes due to symbol-specific tick sizes.
      if(MathAbs(sl - StopLossPrice) > tickSize * 0.001)
      {
         PrintFormat("SKIPPED #%I64u (%s): input SL is not on the symbol's tick grid.", ticket, symbol);
         skipped++;
         continue;
      }
      if(MathAbs(currentSL - sl) < tickSize * 0.5) { skipped++; continue; }

      MqlTick tick;
      if(!SymbolInfoTick(symbol, tick) || tick.bid <= 0 || tick.ask <= 0)
      {
         PrintFormat("FAILED #%I64u: market quote unavailable.", ticket);
         failed++;
         continue;
      }

      int stops = (int)SymbolInfoInteger(symbol, SYMBOL_TRADE_STOPS_LEVEL);
      int freeze = (int)SymbolInfoInteger(symbol, SYMBOL_TRADE_FREEZE_LEVEL);
      double minDistance = (double)MathMax(stops, freeze) * point;
      bool valid = (type == POSITION_TYPE_BUY)
                   ? (sl < tick.bid && tick.bid - sl > minDistance)
                   : (sl > tick.ask && sl - tick.ask > minDistance);
      if(!valid)
      {
         PrintFormat("SKIPPED #%I64u (%s): SL %.*f is invalid/too close for this %s position.",
                     ticket, symbol, digits, sl, type == POSITION_TYPE_BUY ? "BUY" : "SELL");
         skipped++;
         continue;
      }

      ResetLastError();
      bool sent = trade.PositionModify(ticket, sl, tp); // preserves existing TP
      uint retcode = trade.ResultRetcode();
      if(sent && retcode == TRADE_RETCODE_DONE)
      {
         updated++;
         PrintFormat("UPDATED #%I64u (%s): SL=%.*f", ticket, symbol, digits, sl);
      }
      else
      {
         failed++;
         PrintFormat("FAILED #%I64u (%s): retcode=%u (%s), lastError=%d",
                     ticket, symbol, retcode, trade.ResultRetcodeDescription(), GetLastError());
      }
   }
   string result = StringFormat("SL bulk update complete. Updated: %d | Skipped: %d | Failed: %d", updated, skipped, failed);
   Print(result);
   Alert(result);
}
