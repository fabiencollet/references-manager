// Get the modal
var line_tags = document.getElementById('stacked-tags');

// Get the image and insert it inside the modal - use its "alt" text as a caption

function setToggleTag(){

    var available_tags = document.getElementsByClassName("available-tag");

    for (i = 0; i < available_tags.length; i++){


        available_tags[i].onclick = function(){
            var split_class = this.className.split(" active");

            if(split_class.length > 1){

                var class_before = this.className;
                var class_after = class_before.replace(" active", "");

                this.className = class_after;

                var line_before = line_tags.value;
                var line_before_array = line_before.split(",");
                var line_after_array = [];
                for (a = 0; a < line_before_array.length; a++){
                    if(line_before_array[a] !== this.innerHTML){
                        line_after_array.push(line_before_array[a]);
                    }
                }

                line_tags.value = line_after_array.join(",");

            }

            else{

                this.className += " active";

                if(line_tags.value === ""){
                    var line_array = [];
                }
                else{
                    var line_before = line_tags.value;
                    var line_array = line_before.split(",");
                }

                line_array.push(this.innerHTML);
                line_tags.value = line_array.join(",");

            }

        }
    }
}

setToggleTag();