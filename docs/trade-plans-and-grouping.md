# Trade plans and grouped trading ideas

Open **Journal**, select **My saved journal** and the correct **Journal source**. The **Trade plans & ideas** panel is above the performance report. It covers all dates in that source, independently of the selected month.

## Before entry

1. Choose **New trade plan**.
2. Record a title, exact instrument, direction, setup, planned entry, original stop/target, total idea risk budget in USD, and entry reason/invalidation.
3. Choose **Save original plan**. The server stores an immutable plan and save timestamp. It does not place an order or calculate/enforce exposure.
4. The app captures up to60 completed M5 candles already in its matching local broker archive, ending no later than save time. Missing context stays unavailable; old context is labeled stale. This is saved plan-time candle context, NOT an entry-time screenshot, tick capture, or proof of execution. Synthetic replay never receives substituted broker candles.
5. Enter/manage your trade yourself in MT5 demo. The existing journal exporter imports executions.

Original plan fields cannot be edited or backdated through the app. Create a new plan for a revised idea. Existing post-trade reflection/edit fields do not overwrite the original.

## Link entries and partial exits

Expand **Unassigned positions / executions** and select a matching plan in **Trading idea**. Grouping is limited to the same source, instrument and direction. A hedge/opposite direction needs a separate idea. Multiple positions can be assigned to one idea.

MT5 links follow the stable POSITION_IDENTIFIER, not the transient open-row or exit-deal ID. Existing and subsequently imported partial exits and remaining open volume therefore follow the position automatically. Manual/engine/sample records use individual execution IDs. Group assignment/movement/unassignment is logged separately, without changing imported trades.

To move or unassign a position, expand a card's **Executions & grouping** and change its selector. Choosing **Unassigned** restores it to the unassigned list. No broker action occurs.

A saved plan is labeled **Saved before all linked entries** only if its server save time is no later than every linked entry timestamp. A plan saved after even one linked entry is labeled **Retrospective for one or more entries**. Linking an old trade later cannot manufacture a pre-entry plan. Manual/sample execution times themselves remain unverified.

## Read group results correctly

- **Closed net P/L** sums the same closed journal fills, with the importer's existing cost allocation.
- **Floating P/L** is separate, MT5-reported and excludes swap/commissions/fees. Stale imported snapshots are marked. Other sources do not fabricate floating values.
- Closed fills and open remainders show their own volumes; they are not counted as independent full positions. One MT5 position may have several execution rows.
- Position/idea summaries cover all linked dates. Calendar, monthly reports and performance score continue to count execution rows on their existing closing dates. Grouping never adds extra P/L or changes report totals.
- The risk budget is a trader declaration, not calculated current risk, margin availability or a promise that losses are capped.

## Post-trade review and export

A linked immutable plan is included as evidence in that trade's postmortem. If no separate review-note plan exists, it supplies initial stop/target/setup/reason. If later review notes override risk levels for calculations, the displayed risk-basis label identifies those as retrospective; the original remains unchanged. Existing AI payload preview/consent applies to the linked plan too. No automatic AI request is made.

**Export ideas** downloads source-specific plans, saved contexts, grouping and execution summaries. Monthly journal exports remain execution-based. Include journal_ideas, journal_idea_links and journal_idea_link_audit in normal SQLite backups, alongside the journal and postmortem tables.

Fictional dropdown demo datasets remain read-only and never create saved plans. Browser QA uses a separate fictional database. This remains the current single-workspace app; deployment and separate users are not added by this feature.
