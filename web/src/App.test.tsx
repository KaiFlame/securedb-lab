import {render,screen,fireEvent,waitFor,cleanup} from '@testing-library/react';
import {afterEach,beforeEach,describe,it,expect,vi} from 'vitest';
import App from './App';
afterEach(()=>{cleanup();vi.restoreAllMocks();location.hash='';});
beforeEach(()=>{vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:false,json:async()=>({detail:'Não autenticado'})}));});
describe('Acesso e honestidade da interface',()=>{
 it('apresenta login sem números de segurança fabricados',async()=>{render(<App/>);expect(await screen.findByRole('heading',{name:'Entre no laboratório.'})).toBeVisible();expect(screen.getByLabelText('Senha')).toHaveAttribute('type','password');expect(screen.queryByText('20 / 20')).not.toBeInTheDocument();});
 it('exibe falha de login retornada pelo backend',async()=>{render(<App/>);await screen.findByLabelText('Senha');fireEvent.change(screen.getByLabelText('Senha'),{target:{value:'incorreta'}});fireEvent.click(screen.getByRole('button',{name:/Acessar laboratório/}));expect(await screen.findByRole('alert')).toHaveTextContent('Não autenticado');});
 it('mantém controles pendentes e mostra a empresa autenticada',async()=>{vi.mocked(fetch).mockImplementation(async(input)=>{if(String(input).endsWith('/events'))return {ok:true,json:async()=>[]} as Response;if(String(input).endsWith('/auth/me'))return {ok:true,json:async()=>({id:'1',username:'aurora.leitor',tenant_name:'Aurora Comércio',tenant_id:'A',role:'viewer',csrf:'csrf'})} as Response;return {ok:true,json:async()=>({controls:[],tests:[],timestamp:null,environment:'não executado'})} as Response;});render(<App/>);await screen.findByRole('heading',{name:/Configurar é o começo/});expect(screen.getByText('Aurora Comércio')).toBeVisible();expect(screen.getByText('Ainda não executado')).toBeVisible();expect(screen.getByText('Aguardando comprovação')).toBeVisible();});
});
