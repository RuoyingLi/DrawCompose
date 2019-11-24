"use strict;"
var canvas;

function makeDrawCanvas(canvasElement, infoDiv) {
	var lastPt = null;
	var ctx;
	var pointIdx = 0;
	var canvas = {};
	var offset;
	var points = new Array();
	var paths = new Array();

	canvas.points = points;
	canvas.paths = paths;
	ctx = canvasElement.getContext("2d");
	canvas.storageKeyPrefix = ""
	// Event handler called for each pointerdown event:
	canvas.draw = function (e) {
		var offset = canvasElement.getBoundingClientRect();
		if(lastPt!=null) {
			ctx.beginPath();
			// Start at previous point
			ctx.moveTo(lastPt.x, lastPt.y);
			// Line to latest point
			ctx.lineTo(e.pageX - offset.left, e.pageY - offset.top);
			// Draw it!
			ctx.stroke();
		} else {
			if (typeof canvas.onBeginPath === 'function') {
				canvas.onBeginPath();
			}
		}
		//Store latest pointer
		lastPt = {x:e.pageX - offset.left, y:e.pageY - offset.top};
		if (typeof canvas.onDrawNewPoint === 'function') {
			canvas.onDrawNewPoint(lastPt);
		}

		canvas.points.push(lastPt);
	};


	canvas.getOffset = function(obj) {
		var offsetLeft = 0;
		var offsetTop = 0;
		do {
			if (!isNaN(obj.offsetLeft)) {
				offsetLeft += obj.offsetLeft;
			}
			if (!isNaN(obj.offsetTop)) {
				offsetTop += obj.offsetTop;
			}
		} while(obj = obj.offsetParent );
		return {left: offsetLeft, top: offsetTop};
	};

	canvas.endPointer = function(e) {
		//Stop tracking the pointermove (and mousemove) events
		canvasElement.removeEventListener("pointermove", canvas.draw, false);
		canvasElement.removeEventListener("mousemove", canvas.draw, false);
		console.log("Canvas points: " + JSON.stringify(canvas.points));
		canvas.paths.push(canvas.points);
		if (typeof canvas.onPathFinish === 'function' && canvas.points.length > 0) {
			console.log("Path finished");
            canvas.onPathFinish(canvas.points);
		}
		points = new Array()
		canvas.points = points;
		//Set last point to null to end our pointer path
		lastPt = null;
	};

	if(window.PointerEvent) {
		canvasElement.addEventListener("pointerover", function(e) {
			infoDiv.innerHTML = "pointerover" + e.pointerId;
		});
		canvasElement.addEventListener("pointerleave", function(e) {
			infoDiv.innerHTML = "pointerleft" + e.pointerId;
			canvas.endPointer(e);
		});
		canvasElement.addEventListener("pointerdown", function() {
			canvasElement.addEventListener("pointermove", canvas.draw, false);
		}
			, false);
		canvasElement.addEventListener("pointerup", canvas.endPointer, false);
	}
	else {
		//Provide fallback for user agents that do not support Pointer Events
		canvasElement.addEventListener("mousedown", function() {
			canvasElement.addEventListener("mousemove", canvas.draw, false);
		}
			, false);
		canvasElement.addEventListener("mouseup", canvas.endPointer, false);
	}

	canvas.reDraw = function (){
		canvas.paths.forEach(canvas.drawPointArray);
	};

	canvas.resize = function () {
		var offset = canvasElement.parentElement.getBoundingClientRect();
		var fillStyle = ctx.fillStyle;
		ctx.fillStyle = "blue";
		ctx.fillRect(0, 0, canvasElement.width, canvasElement.height);
		ctx.fillStyle = fillStyle;
		//canvasElement.width = document.documentElement.clientWidth-50;
		//canvasElement.height = document.documentElement.clientHeight-50;
		canvas.reDraw();
	};
	window.addEventListener("resize", canvas.resize, false);

	canvas.drawPointArray = function(points) {
		//console.log("Drawing PointArray: " + JSON.stringify(points));
		if(points.length < 1) {
			console.log("Nothing to draw");
			return;
		}
		ctx.beginPath();
		ctx.moveTo(points[0].x, points[0].y);
		for (var idx=1; idx < points.length; idx++) {
			ctx.lineTo(points[idx].x, points[idx].y);
		}
		ctx.stroke();
		//canvas.paths.push(points);
	};

	canvas.resetCanvas = function() {
		console.log("Resetting canvas");	
		var fillStyle = ctx.fillStyle;
		ctx.fillStyle = "blue";
		ctx.fillRect(0, 0, canvasElement.width, canvasElement.height);
		ctx.fillStyle = fillStyle;

	};

	return canvas;
}

function send_strokes(paths) {
	var strokes = paths;
	fetch("/strokes", {
		method: "post",
		headers: {
			'Accept': 'application/json',
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(strokes)
	});
}


function makeObjectDiv(posX, posY, data) {

}


function init() {
	console.log("Initialize canvas...");
	infoDiv = document.getElementById("infoDiv");
	canvas = makeDrawCanvas(document.getElementById("drawCanvas1"), infoDiv, localStorage);

	var committed_objects = [];
	var drawingKey = "DrawingPaths";

	localforage.getItem("CurrentDrawing").then(localforage.getItem)
		.then( function(paths) {
			if (paths) {
				console.log("Loaded " + paths.length + " paths from local storage!");
				canvas.paths = paths;
				paths.forEach(canvas.drawPointArray);
			}

			canvas.onDrawNewPoint = function(point) {
			};

			canvas.onBeginPath = function() {
				console.log("Beginning new Path");
			};

			canvas.onPathFinish = function(path) {
				console.log("Path finished" + JSON.stringify(path));
				localforage.setItem("DrawingPaths", canvas.paths);
				console.log("Posting strokes to Server");
				send_strokes(canvas.paths);
			};

			canvas.resize();

		}).catch(function(err) {
			console.log("ERROR loading drawing: " + err);
		});

	document.getElementById("commitButton").addEventListener("click", (e) => {
		console.log("Commit");
		var paths = canvas.paths;
		committed_objects.push(paths);
		canvas.paths = new Array();
		fetch("/command", {
			method: "post",
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({cmd: "commit"})
		});
		//make
	});

	document.getElementById("undoButton").addEventListener("click", (e) => {
		console.log("undo");
		fetch("/command", {
			method: "post",
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({cmd: "undo"})
		});
		canvas.resetCanvas();
	});
}

window.addEventListener("load", function(e) {
	init();
}, false);
