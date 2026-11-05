import {useState} from 'react';
import {Sun,Moon} from 'lucide-react';
export default function ThemeToggle(){
 const [light,setLight]=useState(()=>document.documentElement.dataset.theme==='light');
 function toggle(){const next=!light;setLight(next);document.documentElement.dataset.theme=next?'light':'dark';try{localStorage.setItem('tradelens.theme',next?'light':'dark')}catch{}}
 return <button className="theme-toggle" type="button" onClick={toggle} aria-label={light?'Switch to dark mode':'Switch to light mode'} title={light?'Switch to dark mode':'Switch to light mode'}>{light?<Moon size={17}/>:<Sun size={17}/>}<span>{light?'Dark mode':'Light mode'}</span></button>;
}
