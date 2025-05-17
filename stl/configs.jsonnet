local brick = function(x,y,z) { 
  kind: 'Brick',
  name: self.kind + '-' + x + 'x' + y,
  size: '%s' % [[x, y, z]],
};

local plate = function(x,y) brick(x,y, 0.25) + { 
  kind: 'Plate',
};

local wall = function(x) brick(x, 1 , 4) + { 
  kind: 'Wall',
};

{ 
  ["Plate/" + plate(x,y).name]: plate(x,y) for x in [1,2,3,4,5,6,7,8] for y in [1,2,3,4,5,6,7,8] if x >= y 
  + 
  ["Wall/" + wall(x).name]: wall(x) for x in [1,2,3,4,5,6,7,8],
  fileFormatVersion: '1'
}