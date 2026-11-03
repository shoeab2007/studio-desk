const BOOK_ID = '1XR4TTzxT5zkNootj3GP55ofsWrY3Ha7hjCvHJ4npIqM';
const FIELDS = ['id','client','project','contact','source','service','stage','value','paid','deadline','due','next','approver','hours','revisions','notes','checks'];
const STAGES = ['Lead','Qualified','Proposal','Advance received','Brief approved','Design','Review','Final payment','Delivered','Follow-up','Closed / lost'];
function ownerOnly_() {
  const email=Session.getActiveUser().getEmail();
  const owner=DriveApp.getFileById(BOOK_ID).getOwner().getEmail();
  if(!email || email.toLowerCase()!==owner.toLowerCase()) throw new Error('Only the spreadsheet owner can access Studio Desk. Sign into the owner Google account.');
}
function doGet(){ownerOnly_();return HtmlService.createHtmlOutputFromFile('Index').setTitle('Studio Desk').addMetaTag('viewport','width=device-width, initial-scale=1');}
function sheet_(){return SpreadsheetApp.openById(BOOK_ID).getSheetByName('Projects');}
function snapshot_(){
  const s=sheet_(), rows=s.getDataRange().getValues();
  if(JSON.stringify(rows[0])!==JSON.stringify(FIELDS))throw new Error('Projects headers changed. Restore the original column names.');
  const records=rows.slice(1).filter(row=>row[0]).map(row=>Object.fromEntries(FIELDS.map((k,i)=>[k,k==='checks'?JSON.parse(row[i]||'[]'):['value','paid','hours','revisions'].includes(k)?Number(row[i]||0):String(row[i]??'')])));
  const revision=Utilities.base64EncodeWebSafe(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,JSON.stringify(rows)));
  return {revision,records};
}
function getState(){ownerOnly_();const lock=LockService.getScriptLock();lock.waitLock(10000);try{return snapshot_();}finally{lock.releaseLock();}}
function validRecords_(records){
 if(!Array.isArray(records)||records.length>1000)throw new Error('Maximum 1,000 projects.');
 const ids=new Set();
 records.forEach(r=>{
  if(!r||typeof r.id!=='string'||!/^[-a-zA-Z0-9_]{1,100}$/.test(r.id)||ids.has(r.id))throw new Error('Invalid or duplicate project ID.');ids.add(r.id);
  if(!STAGES.includes(r.stage))throw new Error('Invalid stage.');
  FIELDS.filter(k=>!['checks','value','paid','hours','revisions'].includes(k)).forEach(k=>{if(typeof r[k]!=='string'||r[k].length>20000)throw new Error('Invalid field: '+k);});
  ['value','paid','hours','revisions'].forEach(k=>{if(typeof r[k]!=='number'||!Number.isFinite(r[k])||r[k]<0)throw new Error('Invalid amount: '+k);});
  if(r.paid>r.value)throw new Error('Received exceeds fee.');
  if(!Array.isArray(r.checks)||!r.checks.every(v=>Number.isInteger(v)&&v>=0&&v<=10))throw new Error('Invalid checkpoints.');
 });
}
function saveState(payload){
 ownerOnly_();validRecords_(payload.records);
 const lock=LockService.getScriptLock();lock.waitLock(10000);
 try{
  const current=snapshot_();if(current.revision!==payload.revision)throw new Error('Another device or sheet edit changed the records. Export your unsaved backup, reload, and reconcile.');
  const s=sheet_(), rows=payload.records.map(r=>FIELDS.map(k=>k==='checks'?JSON.stringify(r[k]):typeof r[k]==='string'?(/^[=+@\-']/.test(r[k])?"'"+r[k]:r[k]):r[k]));
  const height=Math.max(rows.length,s.getLastRow()-1,1);
  while(rows.length<height)rows.push(FIELDS.map(()=>''));
  if(s.getMaxRows()<height+1)s.insertRowsAfter(s.getMaxRows(),height+1-s.getMaxRows());
  s.getRange(2,1,height,FIELDS.length).setNumberFormat('@').setValues(rows);
  SpreadsheetApp.flush();return {revision:snapshot_().revision};
 }finally{lock.releaseLock();}
}
