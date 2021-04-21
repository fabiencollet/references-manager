// Get the modal
var color_preview = document.getElementsByClassName('color_preview');
var text_color_preview = document.getElementsByClassName('text_color_preview');


var hue = document.getElementById('hue');
var saturation = document.getElementById('saturation');
var light = document.getElementById('value');

var hue_text = document.getElementById('hue_text');
var saturation_text = document.getElementById('saturation_text');
var light_text = document.getElementById('value_text');

hue_text.innerHTML = hue.value;
saturation_text.innerHTML = saturation.value;
light_text.innerHTML = light.value;

hue.oninput  = function() {
    showColor();
}

saturation.oninput  = function() {
    showColor();
}

light.oninput  = function() {
    showColor();
}

showColor();

function showColor() {
    var rgb = hsvToRgb(hue.value/12, saturation.value, light.value);
    for (i = 0; i < color_preview.length; i++){
        if(light.value >= 1 && saturation.value <= 0.1){
            color_preview[i].style = "background-color: rgb("+rgb[0]+","+rgb[1]+","+rgb[2]+"); color: grey";
        }
        else if(hue.value >= 2 && hue.value <= 6 && light.value >= 0.9){
            color_preview[i].style = "background-color: rgb("+rgb[0]+","+rgb[1]+","+rgb[2]+"); color: grey";
        }
	    else{
	        color_preview[i].style = "background-color: rgb("+rgb[0]+","+rgb[1]+","+rgb[2]+"); color: white";
	    }
    for (i = 0; i < color_preview.length; i++){
        text_color_preview[i].style = "color: rgb("+rgb[0]+","+rgb[1]+","+rgb[2]+")";
        }
    }

    hue_text.innerHTML = hue.value;
    saturation_text.innerHTML = saturation.value;
    light_text.innerHTML = light.value;
}

function hsvToRgb(h, s, v) {
  var r, g, b;

  var i = Math.floor(h * 6);
  var f = h * 6 - i;
  var p = v * (1 - s);
  var q = v * (1 - f * s);
  var t = v * (1 - (1 - f) * s);

  switch (i % 6) {
    case 0: r = v, g = t, b = p; break;
    case 1: r = q, g = v, b = p; break;
    case 2: r = p, g = v, b = t; break;
    case 3: r = p, g = q, b = v; break;
    case 4: r = t, g = p, b = v; break;
    case 5: r = v, g = p, b = q; break;
  }

  return [ r * 255, g * 255, b * 255 ];
}