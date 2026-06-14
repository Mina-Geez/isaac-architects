const nav=document.getElementById('nav');
if(nav)window.addEventListener('scroll',()=>{nav.classList.toggle('scrolled',window.scrollY>80)});

const hamburger=document.getElementById('hamburger');
const mobileMenu=document.getElementById('mobileMenu');
const menuClose=document.getElementById('menuClose');
function setMenu(open){
  mobileMenu.classList.toggle('open',open);
  document.body.style.overflow=open?'hidden':'';
  hamburger.setAttribute('aria-expanded',open?'true':'false');
}
hamburger.addEventListener('click',()=>setMenu(true));
if(menuClose)menuClose.addEventListener('click',()=>setMenu(false));
mobileMenu.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>setMenu(false)));

const toTop=document.getElementById('toTop');
if(toTop){
  const onScroll=()=>toTop.classList.toggle('show',window.scrollY>600);
  window.addEventListener('scroll',onScroll,{passive:true});onScroll();
  toTop.addEventListener('click',()=>{
    const rm=window.matchMedia('(prefers-reduced-motion:reduce)').matches;
    window.scrollTo({top:0,behavior:rm?'auto':'smooth'});
  });
}

const observer=new IntersectionObserver(entries=>{
  entries.forEach(e=>{if(e.isIntersecting)e.target.classList.add('visible')});
},{threshold:.1,rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.reveal').forEach(el=>observer.observe(el));

document.querySelectorAll('.filter-btn').forEach(btn=>{
  btn.addEventListener('click',()=>{
    document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    const f=btn.dataset.filter;
    document.querySelectorAll('.project-card').forEach(card=>{
      if(f==='all'||card.dataset.category===f){
        card.style.display='';
        requestAnimationFrame(()=>{
          card.classList.remove('visible');
          requestAnimationFrame(()=>card.classList.add('visible'));
        });
      }else{card.style.display='none'}
    });
  });
});

const filterSelect=document.getElementById('filterSelect');
if(filterSelect){
  filterSelect.addEventListener('change',()=>{
    const btn=document.querySelector('.filter-btn[data-filter="'+filterSelect.value+'"]');
    if(btn)btn.click();
  });
}

document.querySelectorAll('a[href^="#"]').forEach(a=>{
  a.addEventListener('click',e=>{
    e.preventDefault();
    const t=document.querySelector(a.getAttribute('href'));
    if(t)t.scrollIntoView({behavior:'smooth',block:'start'});
  });
});

/* Enquiry form. Works immediately by composing an email to the studio.
   To deliver submissions straight to the inbox (no email app needed), create a
   free form at formspree.io and paste its id below — e.g. FORMSPREE_ID='xeoqybgr'. */
const FORMSPREE_ID='';
const enq=document.getElementById('enquiryForm');
if(enq){
  enq.addEventListener('submit',e=>{
    e.preventDefault();
    const note=document.getElementById('formNote');
    const fd=new FormData(enq);
    const name=(fd.get('name')||'').trim();
    const contact=(fd.get('contact')||'').trim();
    const type=fd.get('type')||'';
    const msg=(fd.get('message')||'').trim();
    if(!name||!contact){note.textContent='Please add your name and how to reach you.';return;}
    if(FORMSPREE_ID){
      const btn=enq.querySelector('button');btn.disabled=true;note.textContent='Sending…';
      fetch('https://formspree.io/f/'+FORMSPREE_ID,{method:'POST',body:fd,headers:{Accept:'application/json'}})
        .then(r=>{if(r.ok){enq.reset();note.textContent='Thank you — we’ll be in touch shortly.';}
                  else{note.textContent='Something went wrong. Please call or WhatsApp us.';}})
        .catch(()=>{note.textContent='Something went wrong. Please call or WhatsApp us.';})
        .finally(()=>{btn.disabled=false;});
    }else{
      const subject='Project enquiry from '+name;
      const body='Name: '+name+'\nContact: '+contact+'\nProject type: '+type+'\n\n'+msg;
      window.location.href='mailto:ideadesigns.arch@gmail.com?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);
      note.textContent='Opening your email app…';
    }
  });
}
