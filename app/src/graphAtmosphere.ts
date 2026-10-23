// Deterministic decorative stars: no trading meaning and no random layout jumps.
export const atmosphereStars=Array.from({length:72},(_,i)=>({
 x:18+((i*137.508+i*i*3.17)%804),y:12+((i*97.31+i*i*1.37)%496),
 depth:i%3,radius:.35+(i%5)*.13,phase:i*2.399963,opacity:.16+(i%4)*.045
}));
export function atmospherePoint(star:typeof atmosphereStars[number],time:number){
 const rate=.025+star.depth*.012;
 return {x:star.x+Math.sin(time*rate+star.phase)*(4+star.depth*4),y:star.y+Math.cos(time*rate*.7+star.phase)*(3+star.depth*2),opacity:star.opacity*(.8+.2*Math.sin(time*.18+star.phase))};
}

// One brief streak per 22-second window, with a varying start time and path.
export function shootingStar(time:number){
 const cycle=Math.floor(Math.max(0,time)/22),start=4+((cycle*3.73)%7),progress=(time-cycle*22-start)/1.25;
 const active=progress>0&&progress<1,t=Math.max(0,Math.min(1,progress));
 return {x:70+((cycle*131)%340)+t*235,y:35+((cycle*43)%120)+t*125,opacity:active?Math.sin(Math.PI*t)*.65:0};
}
