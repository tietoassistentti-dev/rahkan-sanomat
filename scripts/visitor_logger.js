// Update login.html script
const visitor = { time: new Date().toLocaleString(), ua: navigator.userAgent.split(' ')[0] };
let visitors = JSON.parse(localStorage.getItem('rs_visitors') || '[]');
visitors.unshift(visitor); 
if (visitors.length > 5) visitors.pop(); 
localStorage.setItem('rs_visitors', JSON.stringify(visitors));
