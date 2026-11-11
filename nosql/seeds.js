(()=>{
const seedLab = db.getSiblingDB('lab');
const A='11111111-1111-4111-8111-111111111111', B='22222222-2222-4222-8222-222222222222';
const products = [
 {_id:'f1111111-1111-4111-8111-111111111111',tenant_id:A,name:'Estação Compacta Pro',sku:'EQ-001',category:'Equipamentos',price_cents:NumberInt(416000),active:true},
 {_id:'f2222222-2222-4222-8222-222222222222',tenant_id:A,name:'Workspace Essencial',sku:'SW-001',category:'Software',price_cents:NumberInt(62000),active:true},
 {_id:'f3333333-3333-4333-8333-333333333333',tenant_id:A,name:'Diagnóstico de infraestrutura',sku:'SV-001',category:'Serviços',price_cents:NumberInt(240000),active:true},
 {_id:'f4444444-4444-4444-8444-444444444444',tenant_id:B,name:'Monitor de Operações',sku:'SW-002',category:'Software',price_cents:NumberInt(180000),active:true}
];
for (const p of products) seedLab.products.updateOne({_id:p._id},{$setOnInsert:p},{upsert:true});
for (const p of [
 {_id:'c1111111-1111-4111-8111-111111111111',tenant_id:A,name:'Contato Horizonte',email:'contato.horizonte@example.test',segment:'Corporativo',active:true},
 {_id:'c2222222-2222-4222-8222-222222222222',tenant_id:B,name:'Contato Núcleo',email:'contato.nucleo@example.test',segment:'Estratégico',active:true}
]) seedLab.profiles.updateOne({_id:p._id},{$setOnInsert:p},{upsert:true});
})();
