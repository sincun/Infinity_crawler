!function(){function a(a){return a.toString().replace(/^[^\/]+\/\*!\s*/,"").replace(/\*\/[^\/]+$/,"")}function b(){var a=document.createElement("style"),b="console_active";a.innerHTML=g,q=document.createElement("div"),r=document.createElement("div"),s=document.createElement("div"),q.id="youdao_console",r.className="console_result",s.className="console_btn",s.innerHTML="黑科技",q.appendChild(a),q.appendChild(s),q.appendChild(r),document.body.appendChild(q),s.addEventListener("click",function(a){q.className=q.className===b?"":b},!1)}var c=navigator.userAgent.toLowerCase()||"",d=/ipad/i.test(c),e=/android/i.test(c)&&!/mobile/i.test(c),f=d||e;if(-1!==c.indexOf("mobile")||f){var g=a(function(){/*!
#youdao_console {
  position: fixed;
  z-index: 999999;
  top: 0;
  right: 0;
  font-size: 14px;
  color: #FFF;
  text-align: left;
}
#youdao_console.console_active {
  width: 100%;
  height: 100%;
}
#youdao_console .console_btn {
  position: absolute;
  margin-top: 50px;
  z-index: 3;
  top: 40%;
  right: 0;
  width: 50px;
  height: 50px;
  line-height: 50px;
  text-align: right;
  background-color: rgba(0,0,0,1);
  border-radius: 50px 0 0 50px;
}
#youdao_console .console_result {
  position: absolute;
  left: 130%;
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  background-color: rgba(0,0,0,.7);
  transition: left .3s ease;
  overflow-y: scroll;
}
#youdao_console.console_active .console_result {
  left: 0;
}
#youdao_console .item {
  word-break: break-all;
  padding: .5em;
  list-style: none;
}
#youdao_console .item span {
  padding: 1px .5em 2px;
  border-radius: 8px;
  margin-right: .5em;
  line-height: 150%;
  background-color: rgba(180,180,180, .6);
}
#youdao_console .item .console_num {
  background-color: rgba(255,128,0, .6);
}
#youdao_console .item .console_key {
  background-color: rgba(255,0,0, .6);
}
#youdao_console .item .console_value {
  color: #000;
  background-color: rgba(255,255,0, .6);
}
*/
return""}),h=[],i={},j=i.toString,k=i.hasOwnProperty,l=function(a,b){return k.call(a,b)},m=function(a){return"[object String]"===j.call(a)},n=(Array.isArray||function(a){return"[object Array]"===j.call(a)},h.forEach?function(a,b){a||(a=[]),a.forEach(b)}:function(a,b){a||(a=[]);for(var c=0,d=a.length;d>c;c++)b(a[c],c,a)}),o=(Object.keys||function(a){var b=[];for(var c in a)l(a,c)&&b.push(c);return b},window.console),p=window.console=function(){};n(["memory","debug","error","info","log","warn","dir","dirxml","table","trace","assert","count","markTimeline","profile","profileEnd","time","timeEnd","timeStamp","timeline","timelineEnd","group","groupCollapsed","groupEnd","clear"],function(a,b){p[a]=function(){var b=h.slice.call(arguments,0);o[a].apply(o,b)}});var q,r,s,t=1,u=function(a){return m(a)?a.replace(/</g,"&lt;").replace(/>/g,"&gt;"):a},v=function(a,b){return['<span class="'+b+'">',u(a),"</span>"].join("")},w=function(a){return a=m(a)?a:JSON?JSON.stringify(a):j.call(a),v(a,"console_value")},x=function(){return v(t++,"console_num")};p.log=function(){var a=h.slice.call(arguments,0),b=document.createElement("div"),c=[];o.log.apply(o,a),b.className="item",c.push(x()),n(a,function(a,b){c.push(w(a))}),b.innerHTML=c.join(""),r.insertBefore(b,r.firstChild)},b()}}();