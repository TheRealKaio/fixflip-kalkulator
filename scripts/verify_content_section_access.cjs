'use strict';
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
 for(const viewport of [{width:1280,height:900},{width:390,height:844}]){
 const page=await browser.newPage({viewport});
 await page.setContent(`<style>html:not(.nic-content-ready) [data-nic-content-key]{visibility:hidden!important}</style>`+
 ['budget','own','rent','flip','finance'].map(key=>`<section data-nic-content-key="${key}.test"><button>Action</button><input><button disabled>Native lock</button><strong>123 €</strong></section>`).join(''));
 assert.equal(await page.locator('section').first().evaluate(el=>getComputedStyle(el).visibility),'hidden');
 await page.evaluate(()=>{window.NICAccess={user:null};window.actions=0;document.querySelector('button').addEventListener('click',()=>window.actions++);});
 await page.addScriptTag({path:'assets/content-section-access.js'});
 const apply=async rule=>page.evaluate(rule=>{window.NICSettings={current:{contentSections:Object.fromEntries(['budget','own','rent','flip','finance'].map(key=>[key+'.test',rule]))}};window.NICContentSections.apply(window.NICSettings.current);},rule);
 await apply({visible:false,guestAllowed:true});
 assert.equal(await page.locator('section').evaluateAll(els=>els.every(el=>el.hidden&&el.inert&&getComputedStyle(el).display==='none')),true);
 await page.evaluate(()=>document.querySelectorAll('section').forEach(el=>{el.hidden=false;el.inert=false;el.className='';el.querySelector('button').disabled=false;}));
 await page.waitForFunction(()=>Array.from(document.querySelectorAll('section')).every(el=>el.hidden&&el.inert&&el.querySelector('button').disabled));
 await apply({visible:true,guestAllowed:false});
 assert.equal(await page.locator('section').evaluateAll(els=>els.every(el=>!el.hidden&&el.inert&&el.querySelector('input').disabled&&el.querySelector('.nic-masked-value'))),true);
 await page.evaluate(()=>{document.querySelector('button').dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));document.querySelector('section').insertAdjacentHTML('beforeend','<button id="dynamic">New</button>');});
 assert.equal(await page.evaluate(()=>window.actions),0);
 await page.waitForFunction(()=>document.querySelector('#dynamic').disabled);
 // Replace all markup and try to remove the guest mask, overlay and lock.
 await page.evaluate(()=>{const box=document.querySelector('section');box.className='';box.inert=false;box.innerHTML='<input><button>New</button><strong>456 €</strong>';});
 await page.waitForFunction(()=>{const box=document.querySelector('section');return box.inert&&box.querySelector('input').disabled&&box.querySelector('.nic-masked-value')&&box.querySelector('.nic-content-box-guest-overlay');});
 await page.evaluate(()=>{window.NICAccess.user={id:1};window.dispatchEvent(new Event('nic-auth-changed'));});
 assert.equal(await page.locator('section').evaluateAll(els=>els.every(el=>!el.inert&&!el.querySelector('input').disabled&&!el.querySelector('.nic-content-box-guest-overlay'))),true);
 assert.equal(await page.locator('section').nth(1).locator('button').last().isDisabled(),true);
 await page.evaluate(()=>{window.NICAccess.user=null;window.dispatchEvent(new Event('nic-auth-changed'));});
 assert.equal(await page.locator('input').first().isDisabled(),true);
 await apply({visible:true,guestAllowed:true});
 assert.equal(await page.locator('input').first().isDisabled(),false);
 // A calculator's own hidden/inert state must survive admin rule roundtrips.
 await page.evaluate(()=>{const box=document.querySelector('section');box.hidden=true;box.inert=true;});
 await apply({visible:false,guestAllowed:false});await apply({visible:true,guestAllowed:true});
 assert.equal(await page.locator('section').first().evaluate(el=>el.hidden&&el.inert),true);
 await page.close();
 }
 console.log('Content section access passed on desktop/mobile: prepaint, all five calculators, attribute tampering, dynamic controls, rerender, masking, login/logout and native locks.');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
