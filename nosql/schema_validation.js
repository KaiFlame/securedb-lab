// Loaded only by bootstrap/seed tooling, never from user input.
(()=>{
const tenant = {bsonType: 'string', pattern: '^[a-f0-9-]{36}$'};
const common = {_id: tenant, tenant_id: tenant, name: {bsonType:'string',minLength:3,maxLength:100}, active:{bsonType:'bool'}};
const schemas = {
 products: {bsonType:'object',additionalProperties:false,required:['_id','tenant_id','name','sku','category','price_cents','active'],properties:{...common,
  sku:{bsonType:'string',pattern:'^[A-Z0-9-]{3,32}$'},category:{enum:['Equipamentos','Software','Serviços']},price_cents:{bsonType:'int',minimum:1,maximum:100000000}}},
 profiles: {bsonType:'object',additionalProperties:false,required:['_id','tenant_id','name','email','segment','active'],properties:{...common,
  email:{bsonType:'string',maxLength:150,pattern:'^[A-Za-z0-9_.+-]+@example\\.test$'},segment:{enum:['Essencial','Corporativo','Estratégico']}}}
};
const lab = db.getSiblingDB('lab');
for (const [name,schema] of Object.entries(schemas)) {
 if (!lab.getCollectionNames().includes(name)) lab.createCollection(name,{validator:{$jsonSchema:schema},validationAction:'error',validationLevel:'strict'});
 else lab.runCommand({collMod:name,validator:{$jsonSchema:schema},validationAction:'error',validationLevel:'strict'});
}
lab.products.createIndex({tenant_id:1,sku:1},{unique:true});
lab.profiles.createIndex({tenant_id:1,email:1},{unique:true});
})();
