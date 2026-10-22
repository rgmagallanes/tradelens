import {randomBytes,scrypt as rawScrypt,timingSafeEqual,createHash} from 'node:crypto';
import {promisify} from 'node:util';
const scrypt=promisify(rawScrypt);
export const hash=value=>createHash('sha256').update(value).digest('hex');
export const token=()=>randomBytes(32).toString('base64url');
export function same(a,b){const x=Buffer.from(hash(a)),y=Buffer.from(hash(b));return timingSafeEqual(x,y)}
export async function passwordHash(password){const salt=randomBytes(16).toString('hex');return `${salt}:${(await scrypt(password,salt,64)).toString('hex')}`}
export async function passwordMatches(password,stored){const [salt,encoded]=(stored||'').split(':');const actual=await scrypt(password,salt||'invalid-user-salt',64);return Boolean(encoded)&&same(actual.toString('hex'),encoded)}
export function sessionCookie(req){const cookies=(req.headers.cookie||'').split(';').map(v=>v.trim());return cookies.find(v=>v.startsWith('tl_session='))?.slice(11)||''}
export function originGuard(origin){return(req,res,next)=>{if(['GET','HEAD','OPTIONS'].includes(req.method)||req.path==='/api/device/upload')return next();if(req.get('origin')!==origin)return res.status(403).json({detail:'Request origin rejected.'});if((req.get('content-type')||'').split(';')[0].toLowerCase()!=='application/json')return res.status(415).json({detail:'JSON required.'});next()}}
export async function rate(pool,key,limit,seconds){const now=Math.floor(Date.now()/1000),window=Math.floor(now/seconds)*seconds,k=hash(key+':'+window);await pool.execute('INSERT INTO tl_limits(limit_key,window_start,hits) VALUES(?,?,1) ON DUPLICATE KEY UPDATE hits=hits+1',[k,window]);const [rows]=await pool.execute('SELECT hits FROM tl_limits WHERE limit_key=?',[k]);return rows[0].hits<=limit;}
