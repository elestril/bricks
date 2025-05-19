module texture(file) {
  scale([ 0.2, 0.2, 2.0 / 255 ]) surface(file = file, convexity = 20);
}