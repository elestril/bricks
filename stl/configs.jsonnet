local brick = function(x,y,z) { 
  type: 'Brick',
  kind: '',
  name: self.kind + '-' + x + 'x' + y,
  size: '%s' % [[x, y, z]],
  stl: self.kind + 's/' + self.name + ".stl"
};

local plate = function(x,y) brick(x,y, 0.25) + { 
  kind: 'Plate',
};

local wall = function(x) brick(x, 1 , 4) + { 
  kind: 'Wall',
};

local tile = function(x,y) brick(x,y, 0.25) + { 
  studs: 'false',
  kind: 'Tile',
};



{ parameterSets: 
  {  
  [plate(x,y).name]: plate(x,y) for x in [1,2,3,4,5,6,7,8] for y in [1,2,3,4,5,6,7,8] if x >= y 
  } 
  + 
  { [wall(x).name]: wall(x) for x in [1,2,3,4,5,6,7,8] }
  + 
  {
    [tile(x,y).name]: tile(x,y) for x in [1,2,4] for y in [1,2,4] if x >= y 
  },

  fileFormatVersion: '1'
}