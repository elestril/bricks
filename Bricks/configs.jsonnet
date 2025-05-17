local wall = function(x) { 
  "name": "Wall-" + x + "x1",
  "kind": "Brick",
  "size": "%s" % [[x, 1, 4]],
};

local plate = function(x,y) { 
  "name": "Plate-" + x + "x" + y,
  "kind": "Brick",
  "size": "%s" % [[x, y, 0.25]],
};


{ 
  "parameterSets": {
    [wall(x).name]: wall(x) for x in [1,2,3,4,5,6,7,8] 
  } + { 
    [plate(x,y).name]: plate(x,y) for x in [1,2,3,4,5,6,7,8] for y in [1,2,3,4,5,6,7,8] 
  },
  "fileFormatVersion": "1"
}