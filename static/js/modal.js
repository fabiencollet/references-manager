
var images = document.getElementsByClassName("project-image");
//var images = document.getElementsByTagName('img');

// Get the image and insert it inside the modal - use its "alt" text as a caption

function selectMenu(e){

    var div_options = document.getElementsByClassName("options");

    console.log(div_options);

    if(e.innerHTML == "Select"){
        e.innerHTML = "Close";
        e.className = "pure-button button-error";
    }
    else{
        e.innerHTML = "Select";
        e.className = "pure-button pure-button-primary";
    }

    for (i = 0; i < images.length; i++){

        var split_class = images[i].className.split(" ");

        if(split_class.length > 1){
            div_options[i].style.visibility = "";
            modify_options.style.visibility = "hidden";
            images[i].className = split_class[0];
            images[i].onclick = function(){
                modal.style.display = "block";
                modalImg.src = this.src;
                captionText.innerHTML = this.alt;
            }
        }
        else{
            modify_options.style.visibility = "visible";
            div_options[i].style.visibility ="hidden";

            images[i].className += " to_select";
            images[i].onclick = function(){
                console.log("CLICKED Images");
                var split = this.className.split(" ");
                if(split[1] == "to_select"){
                    this.className = split[0] + " is_select";
                }
                else{
                    this.className = split[0] + " to_select";
                }
            }

        }


    }

}

function editSelected(){

    var urls = [];
    var selected = document.getElementsByClassName("is_select");

    if(selected.length === 0){
        return;
    }

    for (i = 0; i < selected.length; i++){
        var url = selected[i].getAttribute("src");
        urls.push(url);
    }

    document.location.href = "/edit_selected?urls="+urls.join(",");

}


// Get the modal
var modal = document.getElementById('myModal');

// Get the image and insert it inside the modal - use its "alt" text as a caption

var modalImg = document.getElementById("img01");
var captionText = document.getElementById("caption");

for (i = 0; i < images.length; i++){
	images[i].onclick = function(){
	    modal.style.display = "block";
	    modalImg.src = this.src;
	    captionText.innerHTML = this.alt;
	}
}

// Get the <span> element that closes the modal
var span = document.getElementById("close");
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

function selectAll(){

    for (i = 0; i < images.length; i++){
        images[i].className = "project-image is_select";
    }
}

function deselectAll(){

    for (i = 0; i < images.length; i++){
        images[i].className = "project-image to_select";
    }
}

function deleteSelected(){

    var urls = [];
    var selected = document.getElementsByClassName("is_select");

    var txt;
    var r = confirm("Are you sure to delete medias!");
    if (r == true) {
      txt = "You pressed OK!";
    } else {
      txt = "You pressed Cancel!";
      return;
    }

    if(selected.length === 0){
        return;
    }

    for (i = 0; i < selected.length; i++){
        var url = selected[i].getAttribute("src");
        urls.push(url);
    }

    var current_url = document.location.href.split("#")[0];
    console.log(current_url);
    var query_url = current_url.split("?");
    if(query_url.length > 1){
        var delete_query = current_url.split("&delete");
        if(delete_query.length > 1){
            document.location.href = delete_query[0] + "&delete="+urls.join(",");
        }
        else{
            document.location.href = current_url+"&delete="+urls.join(",");
        }
    }
    else{
        document.location.href = current_url+"?delete="+urls.join(",");
    }

}