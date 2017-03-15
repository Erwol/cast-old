/**
 * Created by erwol on 8/07/16.
 */

var svgns = "http://www.w3.org/2000/svg";
var muted = false;
var subtitled = true;
var previousGlance = '0,0';





function iniciaCara() {
    console.log("Iniciamos cargando los atributos de la cara")
	glance();
	blink();
	//bla()
}
function svgNew(elementType)
{
	svg = svgRoot();
	try {
		return svg.createElementNS(svgns, elementType);
	}
	catch(e) {
		// When svg is inline, no svg document, use the html document
		return document.createElementNS(svgns, elementType);
	}
}

function svgRoot()
{
	var container = $(document).find("#faceit")[0];
	// For object and embed
	if (container.contentDocument)
		return container.contentDocument;

	return $(container).contents();
	// Old browsers have getSVGDocument instead
	try { return container.getSVGDocument(); }
	catch(e) {}
	alert("inline");
	// Inline svg
	return $(container).children()[0];
}



	function parpelles(upper, lower) {
		var svg = svgRoot();
		var eyelid = $(svg).find('#eyelid_r');
		var blinkanimation = $(eyelid).find("#blinkanimation")[0];
		if (blinkanimation !== undefined)
			blinkanimation.endElement();
		$(eyelid).attr("d", eyelidsPath(upper, lower));
	}

	function blink() {
		var svg = svgRoot();
		var lids = $(svg).find("#eyelid_r");
		var current = lids.attr("d");
		var blinkanimation = $(lids).find("#blinkanimation")[0];
		if (blinkanimation === undefined)
		{
			blinkanimation = svgNew("animate");
			$(blinkanimation).attr({
				'attributeName': 'd',
				'id': 'blinkanimation',
				'begin': 'indefinite',
				'dur': '0.2s',
				'fill': 'remove',
				});
			$(lids).append(blinkanimation);
		}

		blinkanimation.beginElement();
		nextBlink = Math.random()*3000+400;
		window.setTimeout(blink, nextBlink);
	}

	function glance()
	{
		var svg = svgRoot();
		var eyes = $(svg).find("#eyepupils");
		var eyesanimation = $(eyes).find("#eyesanimation")[0];
		if (eyesanimation === undefined)
		{
			eyesanimation = svgNew("animateMotion");
			$(eyesanimation).attr({
				'id': 'eyesanimation',
				'begin': 'indefinite',
				'dur': '0.3s',
				'fill': 'freeze',
				});
			$(eyes).append(eyesanimation);
		}
		var x = Math.random()*15-7;
		var y = Math.random()*10-5;
		var currentGlance = [x,y].join(',');
		$(eyesanimation).attr('path', "M "+previousGlance+" L "+currentGlance);
		previousGlance = currentGlance;
		eyesanimation.beginElement();
		nextGlance = Math.random()*1000+4000;
		window.setTimeout(glance, nextGlance);
	}

	function mouthPath(openness)
	{
		return encodePath([
			"M",
			[173.28125, 249.5],
			"L",
			[71.5625, 250.8125],
			"C",
			[81.799543, 251.14273],
			[103.83158, 253.0+openness],
			[121.25, 253.0+openness],
			"C",
			[138.66843, 253.0+openness],
			[160.7326, 251.48139],
			[173.28125, 249.5],
			"z"
		]);
	}

function subtitle(text) {
	// Fades out the old text and fades in the new one
	$('#subtitles').animate({opacity:0}, 'fast', 'linear',
			function() {
				$(this)
					.html(text)
					.animate( {opacity:1}, 'normal', 'linear')
					;
			});
}




function encodePath(path) {
	return path.map(function(e) {
		if ($.isArray(e)) return e.join(",");
		return e;
    }).join(" ");
}
function bla() {
	var svg = svgRoot();
	var mouth = $(svg).find("#mouth");
	var blaanimation = $(mouth).find("#blaanimation")[0];
	if (blaanimation === undefined)
	{
		blaanimation = svgNew("animate");
		$(blaanimation).attr({
			'attributeName': 'd',
			'id': 'blaanimation',
			'begin': 'indefinite',
			'dur': '0.3s',
			});
		$(mouth).append(blaanimation);
	}
	var syllable = [
		mouthPath(0),
		mouthPath(10),
		mouthPath(0),
		].join(";");
	var syllables = Math.floor(Math.random()*4)+1;
	$(blaanimation)
		.off()
		.attr('values', syllable)
		.attr('repeatCount', syllables)
//			.on('repeat', sayBla) // Not workin on webkit 537.36
		;
	// subtitle(Array(syllables).join("bla-")+'bla');
	blaanimation.beginElement();
		//sayBla();
	// Hack instead of onrepeat to trigger the syllables

    //for (var i=1; i<syllables; i++)
    // Llama a una función tras un tiempo especificado
    //window.setTimeout(sayBla, i*0.3*1000);

	// Next bla word
	var wordseconds = (syllables+1)*0.3;
	var nextBla = Math.random()*2000+wordseconds*1000;

	//console.log("Mueve boca")
	//window.setTimeout(bla, nextBla);
}