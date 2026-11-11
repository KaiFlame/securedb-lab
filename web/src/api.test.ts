import {afterEach,it,expect,vi} from 'vitest';
import {api} from './api';
afterEach(()=>vi.restoreAllMocks());
it('expiração de sessão notifica a interface para exigir novo login',async()=>{
 const onExpiry=vi.fn();window.addEventListener('securedb:session-expired',onExpiry);
 vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:false,status:401,json:async()=>({detail:'Sessão expirada.'})}));
 await expect(api('/orders')).rejects.toThrow('Sessão expirada.');expect(onExpiry).toHaveBeenCalledOnce();window.removeEventListener('securedb:session-expired',onExpiry);
});
it('senha inválida preserva a mensagem do formulário sem expirar outra sessão',async()=>{
 const onExpiry=vi.fn();window.addEventListener('securedb:session-expired',onExpiry);
 vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:false,status:401,json:async()=>({detail:'Usuário ou senha inválidos.'})}));
 await expect(api('/auth/login')).rejects.toThrow('Usuário ou senha inválidos.');expect(onExpiry).not.toHaveBeenCalled();window.removeEventListener('securedb:session-expired',onExpiry);
});
