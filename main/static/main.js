// Create a 2d canvas
var canvas = document.getElementById('canvas');
var c = canvas.getContext('2d');

// Colors for various elements
var colors = {
  backdrop: '#E6E9ED',
  foreground: '#434A54',
  sliderLateral: '#A0D468',
  sliderVerts: '#FFCE54',
  sliderClaw: '#8067B7',
  sliderSpinman: '#DA4453'
};

// Images used for animations
var imgs = {
  spinman: document.getElementById("img-spinman"),
  claw: document.getElementById("img-claw"),
  hor: document.getElementById("img-spinman"),
  ver: document.getElementById("img-spinman")
};

function rect(color, x,y, w,h) {
	c.fillStyle = color;
	c.fillRect(x,y,w,h);
}

function circ(color, x,y, r) {
	c.beginPath();
	c.arc(x,y, r, 0, 2 * Math.PI);
	c.fillStyle = color;
	c.fill();
}

function renderCanvas() {
  canvas.width = document.body.clientWidth/2;
  canvas.height = document.body.clientHeight;
  var w = canvas.width;
  var h = canvas.height;

  rect(colors.backdrop, 0,0,w,h);
  rect(colors.foreground, 0,0,w,h/2);

  rect(
    colors.sliderLateral,
    0, h/4,
    w/4, -((info.motor[0][0]/100) * h/4));

  rect(
    colors.sliderLateral,
    w/4, h/4,
    w/4, -((info.motor[0][1]/100) * h/4));

  rect(
    colors.sliderVerts,
    w/2, h/4,
    w/4, -((info.motor[1][0]/100) * h/4));

  rect(
    colors.sliderVerts,
    w/1.3333333, h/4,
    w/4, -((info.motor[1][1]/100) * h/4));

  rect(
    colors.sliderClaw,
    0, h/1.3333333,
    w/2, (info.claw/100) * h/4);

  rect(
    colors.sliderSpinman,
    w/2, h/1.3333333,
    w/2, (info.motor[2][0]/100) * h/4);

  //c.drawImage(img,10,10);
}

function render() {
	// variable which is increase by Math.PI every seconds - usefull for animation
	var PIseconds	= Date.now() * Math.PI;

	// animation of all objects
	scene.traverse(function(object3d, i){
		if(object3d instanceof THREE.Mesh === false) return
		//object3d.rotation.y = PIseconds*0.0003 * (i % 2 ? 1 : -1);
		//object3d.rotation.x = PIseconds*0.0002 * (i % 2 ? 1 : -1);
	})

	// render the scene
	renderer.render(scene, camera);
  renderCanvas();
}

var info = {
  motor: [
    [0,0],
    [0,0],
    [0,0]
  ],

  claw: 0
}

// open websocket connection on port 23456 (beacsue port 8888 is blocked)
var ws = new WebSocket("ws://localhost:23456/websocket");
ws.onmessage = function(evt) {
    // when a message is sent from the server save it as sent
    // sent_ are all partial strings to see what id to update
    var sent = evt.data;
    console.log(sent);

    var knownPrefixes = "VHCSBM";
    console.log(knownPrefixes.indexOf(sent[0]));
    if(knownPrefixes.indexOf(sent[0]) >= 0) {
      switch (sent[0]) {
        case 'C':
          info.claw = parseInt(sent.slice(1, sent.length) * 100);
          break;

        case 'M':
          info.motor[parseInt(sent[1])][parseInt(sent[2])] = parseInt(sent.slice(3, sent.length));
          break;
      }
    } else {
      console.log('unknown prefix');
    }
};

var stats, scene, renderer, composer;
var camera, cameraControls;

if(!init())	animate();

// init the scene
function init() {
	if(Detector.webgl) {
		renderer = new THREE.WebGLRenderer( {
			antialias: true
		});
		renderer.setClearColor(0xbbbbbb);
	} else{
		renderer = new THREE.CanvasRenderer();
	}
	renderer.setSize(window.innerWidth/2, window.innerHeight);
	document.getElementById('container').appendChild(renderer.domElement);

	scene = new THREE.Scene();

	camera	= new THREE.PerspectiveCamera(35, (window.innerWidth/2) / window.innerHeight, 1, 10000);
	camera.position.set(0, 0, 5);
	scene.add(camera);

	// transparently support window resize
	THREEx.WindowResize.bind(renderer, camera);

	var light	= new THREE.AmbientLight(0x999999);
	scene.add(light);
	var light	= new THREE.DirectionalLight(0xfffff);
	light.position.set(1, 0.5, 0.1).normalize();
	scene.add(light);
	var light	= new THREE.DirectionalLight(0xffffff);
	light.position.set(0.2, 0.9, 0.6).normalize();
	scene.add(light);
	var light	= new THREE.PointLight(0xffffff);
	light.position.set(-0.5, -0.5, -0.5)
		.normalize().multiplyScalar(1.2);
	scene.add(light);
	var light	= new THREE.PointLight(0xffffff);
	light.position.set(-0.7, -1.1, 0.5)
		.normalize().multiplyScalar(1.2);
	scene.add(light);

	var geometry = new THREE.BoxGeometry(2, 2, 2);
	var material = new THREE.MeshPhongMaterial({ ambient: 0x111111, color: 0x222222 });
	var mesh = new THREE.Mesh(geometry, material);

	mesh.position.z -= 5;
	scene.add(mesh);
}

// animation loop for both 3d and info
function animate() {
	requestAnimationFrame(animate);
	render();
}
