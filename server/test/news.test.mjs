import test from 'node:test';
import assert from 'node:assert/strict';
import {parseFeed,parseCalendar} from '../src/news.mjs';
test('feed preserves attribution and rejects unsafe links and invalid dates',()=>{
 const item=(url,date)=>`<item><title><![CDATA[Gold &amp; rates]]></title><link>${url}</link><pubDate>${date}</pubDate><source>Publisher</source></item>`;
 const result=parseFeed(`<rss>${item('https://example.com/story','Wed, 28 Oct 2026 10:00:00 GMT')}${item('javascript:alert(1)','Wed, 28 Oct 2026 10:00:00 GMT')}${item('https://example.com/invalid','invalid')}</rss>`,{name:'Feed',asset:'Gold',why:'Context'});
 assert.equal(result.length,1);assert.equal(result[0].title,'Gold & rates');assert.equal(result[0].publisher,'Publisher');assert.equal(result[0].published,'2026-10-28T10:00:00.000Z');
 assert.throws(()=>parseFeed('<html>Unavailable</html>',{}));
});
test('calendar uses final meeting day and excludes past dates',()=>{
 const month=(name,days)=>`<div class="fomc-meeting__month"><strong>${name}</strong></div><div class="fomc-meeting__date">${days}</div>`;
 const html=`<h4>2026 FOMC Meetings</h4>${month('September','15-16')}${month('October','27-28')}<h4>2027 FOMC Meetings</h4>${month('January','26-27')}`;
 assert.deepEqual(parseCalendar(html,new Date('2026-10-28T00:00:00Z')).map(x=>x.date),['2026-10-28','2027-01-27']);
 assert.throws(()=>parseCalendar('Unavailable'));
});
