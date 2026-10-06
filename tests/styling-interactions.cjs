/* Exercise the actual slider event handlers without third-party test packages. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const script = html.match(/<script[^>]*>([\s\S]*?)<\/script>/)[1];
new vm.Script(script);
class Element {
  constructor(tag, cls='') { this.tag=tag; this.className=cls; this.children=[]; this.style={}; this.dataset={}; this.events={}; this.attrs={}; this.hover=false; this.rect={top:0,bottom:100}; }
  get classList() { return { contains:n=>this.className.split(' ').includes(n), toggle:(n,on)=>{const set=new Set(this.className.split(' ').filter(Boolean));on?set.add(n):set.delete(n);this.className=[...set].join(' ');} }; }
  appendChild(n) { this.children.push(n); }
  setAttribute(k,v) { this.attrs[k]=v; }
  addEventListener(k,fn) { this.events[k]=fn; }
  querySelectorAll(sel) { return this.children.filter(n=>n.classList.contains(sel.slice(1))); }
  matches() { return this.hover; }
  contains(n) { return n===this; }
  getBoundingClientRect() { return this.rect; }
  fire(name,event={}) { this.events[name]?.({stopPropagation(){},preventDefault(){},...event}); }
}
const work=new Element('section','on');
const intervals=[];
const document={createElement:t=>new Element(t),hidden:false,activeElement:null};
const ctx={document,window:{matchMedia:()=>({matches:false})},innerHeight:844,slideTimers:[],setInterval:(fn,ms)=>{intervals.push({fn,ms});return intervals.length;},clearInterval(){},setTimeout(){},el:(tag,cls)=>new Element(tag,cls),$:()=>work};
vm.createContext(ctx);
vm.runInContext(script.slice(script.indexOf('function makeGeneralCard('),script.indexOf('function placeCurated(')),ctx);
const card=ctx.makeGeneralCard({alt:'Rolex',open:'rolex',slides:['first.jpg','second.jpg','third.jpg'],slideSizes:[[900,600],[800,1000],[800,1000]]});
const ph=card.children[0];
const active=()=>ph.children.findIndex(n=>n.classList.contains('on'));
assert.equal(card.dataset.open,undefined,'Slider click must not open the project');
assert.equal(intervals[0].ms,7500,'Autoplay stays slow');
ph.fire('click');assert.equal(active(),1);
const swipe=(x1,y1,x2,y2)=>{ph.fire('touchstart',{touches:[{clientX:x1,clientY:y1}]});ph.fire('touchmove',{touches:[{clientX:x2,clientY:y2}]});ph.fire('touchend');};
swipe(300,100,50,110);assert.equal(active(),2,'Left swipe advances');
ph.fire('click');assert.equal(active(),2,'Synthetic click following swipe does not advance twice');
swipe(50,100,300,110);assert.equal(active(),1,'Right swipe returns');
ph.fire('click');assert.equal(active(),1);
swipe(200,100,130,350);assert.equal(active(),1,'Vertical scrolling does not advance');
ph.fire('touchstart',{touches:[{clientX:300,clientY:100}]});ph.fire('touchmove',{touches:[{clientX:50,clientY:110}]});ph.fire('touchcancel');ph.fire('touchend');assert.equal(active(),1,'Cancelled gesture does not advance');
ph.fire('keydown',{key:'ArrowRight'});assert.equal(active(),2);
ph.fire('keydown',{key:'ArrowLeft'});assert.equal(active(),1);
document.hidden=true;intervals[0].fn();assert.equal(active(),1,'Hidden document pauses');
document.hidden=false;ph.rect={top:900,bottom:1200};intervals[0].fn();assert.equal(active(),1,'Off-screen carousel pauses');
ph.rect={top:0,bottom:100};intervals[0].fn();assert.equal(active(),2,'Visible carousel autoplays');
ph.hover=true;intervals[0].fn();assert.equal(active(),2,'Hover pauses');
ph.hover=false;document.activeElement=ph;intervals[0].fn();assert.equal(active(),2,'Keyboard focus pauses');
assert.equal(ph.children.filter(i=>i.attrs['aria-hidden']==='false').length,1);
ctx.window.matchMedia=()=>({matches:true});const prior=intervals.length;ctx.makeGeneralCard({alt:'Rolex',slides:['a.jpg','b.jpg']});assert.equal(intervals.length,prior,'Reduced motion disables autoplay');
console.log('PASS: syntax, click, both swipe directions, synthetic-click suppression, vertical scroll, touch cancel, keyboard, autoplay, pause states, reduced motion, active accessibility state.');
