import {database,migrate} from '../src/db.mjs';
const pool=database();try{await migrate(pool);console.log('TradeLens schema is ready.')}finally{await pool.end()}
