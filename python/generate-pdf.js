#!/usr/bin/env node
'use strict';
const { spawn } = require('child_process');
const http      = require('http');
const net       = require('net');
const crypto    = require('crypto');
const path      = require('path');
const fs        = require('fs');

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const [,, htmlArg, pdfArg] = process.argv;
if (!htmlArg || !pdfArg) { console.error('Usage: node generate-pdf.js <input.html> <output.pdf>'); process.exit(1); }
const htmlFile = path.resolve(htmlArg);
const pdfFile  = path.resolve(pdfArg);

function freePort() {
  return new Promise((res, rej) => {
    const s = net.createServer();
    s.listen(0, '127.0.0.1', () => { const p = s.address().port; s.close(() => res(p)); });
    s.on('error', rej);
  });
}
function getJSON(url) {
  return new Promise((res, rej) => {
    http.get(url, r => { let b=''; r.on('data',d=>b+=d); r.on('end',()=>{try{res(JSON.parse(b));}catch(e){rej(e);}}); }).on('error',rej);
  });
}
async function waitForChrome(port, retries=20, interval=300) {
  for (let i=0; i<retries; i++) {
    try { return await getJSON(`http://127.0.0.1:${port}/json/list`); } catch(_) {}
    await new Promise(r=>setTimeout(r,interval));
  }
  throw new Error(`Chrome did not open debug port ${port}`);
}
function wsConnect(wsUrl) {
  return new Promise((resolve, reject) => {
    const u=new URL(wsUrl), key=crypto.randomBytes(16).toString('base64');
    const sock=net.createConnection(parseInt(u.port||80), u.hostname);
    let handshakeDone=false, rxBuf=Buffer.alloc(0);
    const pending=new Map(); let nextId=1;
    sock.on('error',reject);
    sock.on('connect',()=>{
      sock.write(`GET ${u.pathname} HTTP/1.1\r\nHost: ${u.host}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: ${key}\r\nSec-WebSocket-Version: 13\r\n\r\n`);
    });
    sock.on('data',chunk=>{
      rxBuf=Buffer.concat([rxBuf,chunk]);
      if (!handshakeDone) {
        const end=rxBuf.indexOf('\r\n\r\n');
        if (end===-1) return;
        handshakeDone=true; rxBuf=rxBuf.slice(end+4);
      }
      while (rxBuf.length>=2) {
        let pos=0;
        const b0=rxBuf[pos++], b1=rxBuf[pos++];
        const opcode=b0&0x0f, masked=(b1&0x80)!==0;
        let payLen=b1&0x7f;
        if (payLen===126){if(rxBuf.length<pos+2)return; payLen=rxBuf.readUInt16BE(pos);pos+=2;}
        else if(payLen===127){if(rxBuf.length<pos+8)return; payLen=Number(rxBuf.readBigUInt64BE(pos));pos+=8;}
        if(masked)pos+=4;
        if(rxBuf.length<pos+payLen)return;
        const payload=rxBuf.slice(pos,pos+payLen); rxBuf=rxBuf.slice(pos+payLen);
        if(opcode===1){
          let msg; try{msg=JSON.parse(payload.toString());}catch(_){continue;}
          if(msg.id!==undefined&&pending.has(msg.id)){
            const cb=pending.get(msg.id); pending.delete(msg.id);
            if(msg.error)cb.reject(new Error(msg.error.message)); else cb.resolve(msg.result);
          }
        }
      }
    });
    function send(method,params={}){
      return new Promise((res,rej)=>{
        const id=nextId++, txt=JSON.stringify({id,method,params}), buf=Buffer.from(txt), len=buf.length;
        let hdrSize=2; if(len>65535)hdrSize+=8; else if(len>=126)hdrSize+=2;
        const mask=crypto.randomBytes(4), frame=Buffer.alloc(hdrSize+4+len);
        frame[0]=0x81; let off=1;
        if(len>65535){frame[off++]=0x80|127;frame.writeBigUInt64BE(BigInt(len),off);off+=8;}
        else if(len>=126){frame[off++]=0x80|126;frame.writeUInt16BE(len,off);off+=2;}
        else{frame[off++]=0x80|len;}
        mask.copy(frame,off);off+=4;
        for(let i=0;i<len;i++)frame[off+i]=buf[i]^mask[i%4];
        pending.set(id,{resolve:res,reject:rej}); sock.write(frame);
      });
    }
    const check=setInterval(()=>{if(handshakeDone){clearInterval(check);resolve({send,close:()=>sock.destroy()});}},50);
    setTimeout(()=>{clearInterval(check);reject(new Error('WebSocket handshake timeout'));},5000);
  });
}

async function main() {
  const port=await freePort();
  const chrome=spawn(CHROME,['--remote-debugging-port='+port,'--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--no-default-browser-check','about:blank'],{stdio:'ignore'});
  chrome.on('error',e=>{throw e;});
  let ws;
  try {
    const targets=await waitForChrome(port);
    const target=targets.find(t=>t.type==='page')||targets[0];
    ws=await wsConnect(target.webSocketDebuggerUrl);
    await ws.send('Page.enable');
    await ws.send('Page.navigate',{url:`file://${htmlFile}`});
    await new Promise(r=>setTimeout(r,2500));
    const result=await ws.send('Page.printToPDF',{
      printBackground:true, displayHeaderFooter:false,
      marginTop:0, marginBottom:0, marginLeft:0, marginRight:0,
      paperWidth:8.5, paperHeight:11, preferCSSPageSize:false,
    });
    fs.writeFileSync(pdfFile,Buffer.from(result.data,'base64'));
    console.log(`✓  ${pdfFile}  (${Math.round(fs.statSync(pdfFile).size/1024)} KB)`);
  } finally {
    if(ws)ws.close(); chrome.kill();
  }
}
main().catch(e=>{console.error('Error:',e.message);process.exit(1);});
