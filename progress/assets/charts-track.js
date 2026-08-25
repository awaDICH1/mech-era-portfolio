(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();
  var green = '#4ade80', orange = '#fb923c', red = '#f87171', yellow = '#fbbf24', purple = '#a78bfa', pink = '#f472b6';

  var c1 = echarts.init(document.getElementById('chart-todo-pie'), null, { renderer: 'svg' });
  c1.setOption({
    tooltip: { trigger: 'item', appendToBody: true, textStyle: { color: ink } },
    legend: { orient: 'vertical', right: 15, top: 'center', textStyle: { color: muted, fontSize: 12 } },
    series: [{ type:'pie', radius:['32%','70%'], center:['36%','50%'], itemStyle:{borderRadius:8,borderColor:bg2,borderWidth:3}, label:{show:false}, emphasis:{label:{show:true,fontSize:14,fontWeight:'bold',color:ink}}, data:[
      { value:68, name:'无标签占位', itemStyle:{color:muted} },
      { value:61, name:'P5 实体/污染', itemStyle:{color:accent} },
      { value:33, name:'P8 渲染/音效', itemStyle:{color:orange} },
      { value:5, name:'P9 JEI/TOP', itemStyle:{color:green} },
      { value:3, name:'P6 伤害', itemStyle:{color:yellow} },
      { value:2, name:'P7 维度', itemStyle:{color:red} }
    ]}]
  });
  window.addEventListener('resize', function() { c1.resize(); });
})();
