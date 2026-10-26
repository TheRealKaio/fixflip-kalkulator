(function(){
'use strict';
const routes={budget:'/budget/',own:'/eigennutzung/',rent:'/vermietung/',flip:'/fix-flip/',finance:'/finanzierungsrechner/'};
const key='nic_last_calculator_v1';
const current=Object.keys(routes).find(k=>routes[k]===location.pathname);
try{if(current)localStorage.setItem(key,current);}catch(_){}
// Explicit calculator URLs and legal/admin deep links retain their destination.
if(!['/','/index.html'].includes(location.pathname)||location.hash)return;
let selected='finance';try{const saved=localStorage.getItem(key);if(Object.hasOwn(routes,saved))selected=saved;}catch(_){}
location.replace(routes[selected]+location.search);
})();
