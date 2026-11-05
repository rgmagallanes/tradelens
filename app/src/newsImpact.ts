export type NewsImpact = {level:'High'|'Medium'|'Low';reason:string};
/** Editorial topic heuristic, not a measured market reaction or publisher rating. */
export function newsImpact(title:string):NewsImpact {
 if(/\b(fomc|interest.rate decision|rate cut|rate hike|monetary policy|nonfarm|non-farm|payrolls|consumer price index|\bcpi\b|\bpce\b|inflation report|etf approval|etf rejection|exchange hack|exchange collapse|bankruptcy|bitcoin ban|war|invasion)\b/i.test(title))return {level:'High',reason:'Policy, major economic releases, or systemic events can materially change market expectations.'};
 if(/\b(fed|federal reserve|inflation|interest rates|treasury|yields|dollar|etf|regulation|regulator|sec|central bank|reserves|flows|outflows|inflows|tariff|halving|hack)\b/i.test(title))return {level:'Medium',reason:'The topic relates to rates, demand, liquidity, or regulation relevant to these assets.'};
 return {level:'Low',reason:'No major event topic was identified in the headline. This does not establish low actual impact.'};
}
