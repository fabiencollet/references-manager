// Get the modal
var modal = document.getElementById('myModal');

// Get the image and insert it inside the modal - use its "alt" text as a caption

var img = document.getElementsByClassName("project-image");

var modalImg = document.getElementById("img01");
var captionText = document.getElementById("caption");

for (i = 0; i < img.length; i++){
	img[i].onclick = function(){
	    modal.style.display = "block";
	    modalImg.src = this.src;
	    captionText.innerHTML = this.alt;
	}
}

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];
var myModal = document.getElementById("myModal");

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
}
myModal.onclick = function() {
    modal.style.display = "none";
}

document.addEventListener("keydown", echap, false);

function echap(e) {
var keyCode = e.keyCode;
  if(keyCode==27) {
  modal.style.display = "none";
  } 
}