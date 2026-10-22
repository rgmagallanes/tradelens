import mysql from 'mysql2/promise';
import {readFile} from 'node:fs/promises';
export function database(env=process.env){
 for(const name of ['DB_HOST','DB_NAME','DB_USER','DB_PASSWORD'])if(!env[name])throw Error(`Missing ${name}. Configure it privately on the server.`);
 return mysql.createPool({host:env.DB_HOST,port:Number(env.DB_PORT||3306),database:env.DB_NAME,user:env.DB_USER,password:env.DB_PASSWORD,connectionLimit:5,connectTimeout:10000,charset:'utf8mb4',supportBigNumbers:true,bigNumberStrings:true,...(env.DB_SSL==='true'?{ssl:{rejectUnauthorized:true}}:{})});
}
export async function migrate(pool){const sql=await readFile(new URL('./schema.sql',import.meta.url),'utf8');for(const statement of sql.split(';').map(s=>s.trim()).filter(Boolean))await pool.query(statement);}
export async function transaction(pool,fn){const c=await pool.getConnection();try{await c.beginTransaction();const result=await fn(c);await c.commit();return result}catch(e){await c.rollback();throw e}finally{c.release()}}
