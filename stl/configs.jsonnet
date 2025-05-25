local brick = function(kind, x,y,z) { 
  class: 'Brick',
  kind: kind,
  name: self.kind + '-' + x + 'x' + y,
  size: '%s' % [[x, y, z]],
  stl: self.kind + 's/' + self.name + '.stl'
};

local hex = function(class, kind, x,z) brick(kind, x, 0, z) + { 
  class: class,
  name: self.kind + '-' + self.class + '-' + x,
  size: '%s' % [[x, 0, z]],
  stl: 'Hex-' + self.kind + 's/' + self.name + '.stl'
};

{ parameterSets: 
  {  
  [ brick('Plate',x,y,0.25).name]: brick('Plate',x,y,0.25) for x in [1,2,3,4,5,6,7,8] for y in [1,2,3,4,5,6,7,8] if x >= y 
  } + { 
    [brick('Wall',x,1,4).name]: brick('Wall', x, 1, 4) for x in [1,2,3,4,5,6,7,8] 
  } + { 
    [brick('LowWall',x,1,2).name]: brick('LowWall', x, 1, 2) for x in [1,2,3,4,5,6,7,8] 
  } + {
    [brick('Tile',x,y, 0.25).name]: brick('Tile', x, y, 0.25) + {studs: false} for x in [1,2,4] for y in [1,2,4] if x >= y 
  } + { 
    [hex('Hex-R','Plate',x,0.25).name]: hex('Hex-R','Plate', x, 0.25) for x in [0,1,2,3,4,5]
  } + { 
    [hex('Hex-S','Plate',x,0.25).name]: hex('Hex-S','Plate', x, 0.25) for x in [1,2,3,4,5]
  },
  fileFormatVersion: '1'
}