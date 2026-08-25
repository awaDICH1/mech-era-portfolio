(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();
  var green = '#4ade80', orange = '#fb923c', red = '#f87171', yellow = '#fbbf24', purple = '#a78bfa', pink = '#f472b6';

  // Resource Pie
  var c1 = echarts.init(document.getElementById('chart-resource-dist'), null, { renderer: 'svg' });
  c1.setOption({
    tooltip: { trigger: 'item', appendToBody: true, textStyle: { color: ink } },
    legend: { orient: 'vertical', right: 15, top: 'center', textStyle: { color: muted, fontSize: 12 } },
    series: [{ type: 'pie', radius: ['38%', '72%'], center: ['36%', '50%'], itemStyle: { borderRadius: 8, borderColor: bg2, borderWidth: 3 }, label: { show: false }, emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold', color: ink } }, data: [
      { value: 6772, name: 'Textures 纹理', itemStyle: { color: accent } }, { value: 4278, name: 'Models 模型', itemStyle: { color: accent2 } },
      { value: 1125, name: 'BlockStates', itemStyle: { color: green } }, { value: 549, name: 'Sounds 音效', itemStyle: { color: orange } },
      { value: 158, name: 'Manual 手册', itemStyle: { color: yellow } }, { value: 101, name: 'Shaders 着色器', itemStyle: { color: red } },
      { value: 76, name: 'Structures', itemStyle: { color: purple } }, { value: 33, name: 'Particles', itemStyle: { color: pink } }, { value: 3, name: 'Other', itemStyle: { color: muted } }
    ]}]
  });
  window.addEventListener('resize', function() { c1.resize(); });

  // LOC Bar
  var c2 = echarts.init(document.getElementById('chart-loc-distribution'), null, { renderer: 'svg' });
  c2.setOption({
    tooltip: { trigger: 'axis', appendToBody: true, axisPointer: { type: 'shadow' }, textStyle: { color: ink } },
    grid: { left: '3%', right: '15%', bottom: '3%', top: '5%', containLabel: true },
    xAxis: { type: 'value', axisLine: { lineStyle: { color: rule } }, axisLabel: { color: muted, fontSize: 11 }, splitLine: { lineStyle: { color: rule, type: 'dashed' } } },
    yAxis: { type: 'category', data: ['top','jei','network','potion','render','datagen','interfaces','handler','sound','creativetabs','main','uninos','config','api','util','items','blocks','tileentity','inventory','entity'], axisLine: { lineStyle: { color: rule } }, axisLabel: { color: muted, fontSize: 11 } },
    series: [{ type: 'bar', barWidth: 16, itemStyle: { borderRadius: [0,4,4,0] }, data: [42,47,78,184,198,243,115,321,816,796,1388,713,2605,1471,2733,6827,6676,3363,9533,4505], color: [accent] }]
  });
  window.addEventListener('resize', function() { c2.resize(); });

  // Bubble
  var c3 = echarts.init(document.getElementById('chart-bubble'), null, { renderer: 'svg' });
  c3.setOption({
    tooltip: { trigger: 'item', appendToBody: true, textStyle: { color: ink }, formatter: function(p) { return p.data[3]+'<br/><b>'+p.data[0]+'</b><br/>文件: '+p.data[1]+' | 行数: '+p.data[2]; } },
    grid: { left: '8%', right: '8%', top: '8%', bottom: '12%' },
    xAxis: { name: '文件数', type: 'value', axisLine: { lineStyle: { color: rule } }, axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule, type: 'dashed' } }, nameTextStyle: { color: muted, fontSize: 11 } },
    yAxis: { name: '代码行数', type: 'value', axisLine: { lineStyle: { color: rule } }, axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule, type: 'dashed' } }, nameTextStyle: { color: muted, fontSize: 11 } },
    series: [{ type: 'scatter', symbolSize: function(d){return d[1]*0.8+10;}, data: [
      ['entity',135,4505],['inventory',54,9533],['tileentity',35,3363],['util',34,2733],['api',25,1471],['lib',23,3089],
      ['blocks',20,6676],['config',16,2605],['items',13,6827],['hazard',9,1272],['uninos',7,713],['main',6,1388],
      ['handler',4,321],['packet',3,177],['potion',3,184],['render',3,198],['datagen',3,243],['interfaces',3,115],
      ['jei',2,47],['top',2,42],['sound',2,816],['capability',2,621],['network',1,78],['creativetabs',1,796],['particle',1,86]
    ], itemStyle: { color: accent, opacity: 0.7, borderColor: accent, borderWidth: 1 } }]
  });
  window.addEventListener('resize', function() { c3.resize(); });

  // Progress Gantt
  var c4 = echarts.init(document.getElementById('chart-progress-gantt'), null, { renderer: 'svg' });
  c4.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, textStyle: { color: ink } },
    grid: { left: '12%', right: '5%', top: '5%', bottom: '5%', containLabel: true },
    xAxis: { type: 'value', min:0, max:100, axisLine: { lineStyle: { color: rule } }, axisLabel: { color: muted, formatter: '{value}%' }, splitLine: { lineStyle: { color: rule, type: 'dashed' } } },
    yAxis: { type: 'category', data: ['P9 兼容性','P8 渲染体验','P7 维度兼容','P6 伤害能力','P5 实体污染','P4 配方补全','P3 方块实体','P2 物品配方','P1 方块注册','P0 项目骨架'], axisLine: { lineStyle: { color: rule } }, axisLabel: { color: muted, fontSize: 12 } },
    series: [{ type:'bar', barWidth:20, itemStyle:{borderRadius:[0,4,4,0]}, data:[5,25,30,40,55,100,100,100,100,100].map(function(v,i){return {value:v,itemStyle:{color:v>=100?green:v>=50?accent:v>=30?orange:red}}}), label:{show:true,position:'right',formatter:'{c}%',color:muted,fontSize:12,fontWeight:'600'} }]
  });
  window.addEventListener('resize', function() { c4.resize(); });
})();
