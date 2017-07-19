window.onload = addListeners();

function addListeners(){
    document.getElementById('dxy').addEventListener('mousedown', mouseDown, false);
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
	var div = document.getElementById('dxy');
	div.style.position = 'absolute';
	div.style.top = e.clientY + 'px';
	div.style.left = e.clientX + 'px';
}
