(function(){
'use strict';
const routes={budget:'/budget/',own:'/eigennutzung/',rent:'/vermietung/',flip:'/fix-flip/',finance:'/finanzierungsrechner/'};
const key='nic_last_calculator_v1';
const current=Object.keys(routes).find(k=>routes[k]===location.pathname);
try{if(current)localStorage.setItem(key,current);}catch(_){}
// The bare domain is the home page. Explicit calculator URLs keep their
// destinations; a remembered calculator never redirects a home-page visit.
})();
