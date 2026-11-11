export type User = {id:string;username:string;tenant_id:string;tenant_name:string;display_name:string;role:'editor'|'viewer'|'admin';csrf:string};
export type TestResult={id:string;result:'PASS'|'FAIL'|'SKIP';timestamp:string;objective?:string;observed?:unknown;artifact?:string;controls?:string[]};
export type Control={id:string;lab:'SQL'|'NOSQL';step:number;title:string;category:string;criticality:string;risk:string;residual:string;files:string[];status:'pass'|'fail'|'pending';last_run:string|null;tests:TestResult[];required_tests:string[];implemented:boolean;objective:string;positive:string;negative:string;configuration:{path:string;start_line:number;excerpt:string}};
export type Report={controls:Control[];tests:TestResult[];timestamp:string|null;environment:string};
let csrf='';
export function setCsrf(value:string){csrf=value;}
export async function api<T>(path:string,options:RequestInit={}):Promise<T>{
 const res=await fetch('/api'+path,{...options,credentials:'same-origin',headers:{'Content-Type':'application/json',...(options.method&&options.method!=='GET'?{'X-CSRF-Token':csrf}:{}),...options.headers}});
 if(!res.ok){if(res.status===401&&path!=='/auth/login')window.dispatchEvent(new Event('securedb:session-expired'));const data=await res.json().catch(()=>({detail:'Servidor indisponível.'}));throw new Error(typeof data.detail==='string'?data.detail:'Confira os campos informados. A API recusou os dados.');}
 return res.json();
}
export const money=(value:number|string)=>new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(Number(value));
export const date=(value:string|null)=>value?new Date(value).toLocaleString('pt-BR'):'Ainda não executado';
export const statusLabel={pass:'Comprovado',fail:'Falhou',pending:'Pendente'};
