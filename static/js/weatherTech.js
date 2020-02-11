var div = document.getElementById('parts-des');
var len = document.getElementsByClassName("part-num").length


function addPart() {
  var input = document.createElement('input'),
    button = document.createElement('a');
  
  input.placeholder = "Part #";
  input.className = "part-num input";
  input.name = "part-" + len;
  len ++;
  button.innerHTML = 'X';
  button.style.color = "#ed1e25";
  button.className = "remove";
  // attach onlick event handler to remove button
  button.onclick = removePart;
  
  div.appendChild(input);
  div.appendChild(button);
}

function removePart() {
  // remove this button and its input
  div.removeChild(this.previousElementSibling);
  div.removeChild(this);
}

// attach onclick event handler to add button
document.getElementById('part-add').addEventListener('click', addPart);
// attach onclick event handler to 1st remove button
document.getElementById('remove').addEventListener('click', removePart);

