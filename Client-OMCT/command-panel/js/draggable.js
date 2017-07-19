window.onload = addListeners();

function addListeners(){
    document.getElementById('faketerminal').addEventListener('mousedown', mouseDown, false);
    window.addEventListener('mouseup', mouseUp, false);

}

function mouseUp()
{
    window.removeEventListener('mousemove', divMove, true);
}

function mouseDown(e){
  window.addEventListener('mousemove', divMove, true);
}

function divMove(e){
	var div = document.getElementById('faketerminal');
	div.style.position = 'absolute';
	div.style.top = e.clientY + 'px';
	div.style.left = e.clientX + 'px';
}
