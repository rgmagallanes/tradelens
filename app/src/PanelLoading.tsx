export default function PanelLoading({label="Loading workspace…",compact=false}:{label?:string;compact?:boolean}){
 return <section className={'panel-loading'+(compact?' panel-loading-compact':'')} role="status" aria-live="polite" aria-busy="true"><p>{label}</p><div className="panel-loading-shapes" aria-hidden="true"><div className="panel-loading-metrics"><i/><i/><i/></div><div className="panel-loading-chart"/></div></section>;
}
