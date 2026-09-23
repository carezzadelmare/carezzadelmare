(function(){
  const script=document.createElement('script');
  script.src='eventi/eventi-data.js?v='+Date.now();
  script.onload=function(){
    try{
      const pack=window.CAREZZA_EVENTS;
      if(!pack||!Array.isArray(pack.eventi)||!pack.eventi.length)return;
      D.events=pack.eventi.map(e=>[e.data||'',e.titolo||'',e.localita||'',e.orario||'',e.luogo||'',e.descrizione||'',e.info||'']);
      const originalRender=render;
      render=function(){
        originalRender();
        const grid=document.querySelector('#s0 .grid');
        if(!grid)return;
        grid.innerHTML='';
        D.events.forEach(x=>{
          const details=[x[3],x[4],x[5]].filter(Boolean).join(' · ');
          const info=x[6]?'<p class="event-more"><strong>Info:</strong> '+x[6]+'</p>':'';
          grid.insertAdjacentHTML('beforeend',card('<div class="eventday">'+x[0]+'</div><h3>'+x[1]+'</h3><strong>'+x[2]+'</strong>'+(details?'<p>'+details+'</p>':'')+info+buttons(x[1],x[2])));
        });
      };
      render();
    }catch(e){console.error('Caricamento eventi automatici:',e)}
  };
  document.head.appendChild(script);
})();
