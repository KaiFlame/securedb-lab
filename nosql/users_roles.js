(()=>{
const admin = db.getSiblingDB('admin');
if (!admin.getUser('lab_admin')) admin.createUser({user:'lab_admin',pwd:process.env.MONGO_ADMIN_PASSWORD,roles:[{role:'root',db:'admin'}]});
const lab = db.getSiblingDB('lab');
if (!lab.getRole('catalog_api')) lab.createRole({role:'catalog_api',privileges:[
 {resource:{db:'lab',collection:'products'},actions:['find','insert','update']},
 {resource:{db:'lab',collection:'profiles'},actions:['find','insert','update']}
],roles:[]});
if (!lab.getUser('api_user')) lab.createUser({user:'api_user',pwd:process.env.MONGO_APP_PASSWORD,roles:[{role:'catalog_api',db:'lab'}]});
load('/lab-nosql/schema_validation.js');
load('/lab-nosql/seeds.js');
})();
