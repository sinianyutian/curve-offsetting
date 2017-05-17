# "Offsetting parameterised Bezier curves"

from math import sin,cos,radians

# Preparatory stuff: Simplified affine transforms

# Find a simplified affine transform
def unitize(a,b,c,d):
  # Not going to do rotation here, just translation and scaling for now;
  # assume all points are orthogonal
  return { "dx": -a[0], "dy": -d[1], "scale": float(a[1]-d[1])}

def apply1(a, transform):
  return [ (a[0]+transform["dx"]) / transform["scale"],
           (a[1]+transform["dy"]) / transform["scale"] ]

def unapply1(a, transform):
  return [ (a[0]*transform["scale"])-transform["dx"],
           (a[1]*transform["scale"])-transform["dy"] ]

def applyTransform(bez, transform):
  return map(lambda (z): apply1(z,transform), bez)

def applyInvertedTransform(bez, transform):
  return map(lambda (z): unapply1(z,transform), bez)

# Preparatory stuff: Determining curve tension
# (Mostly stolen with modification from mekkablue)

# We could simplify this dramatically given that we're expecting
# orthogonality, but hey, generalize first and things are free later.
def lineLineIntersection(a,b,c,d):
  xdiff = (a[0] - b[0], c[0] - d[0])
  ydiff = (a[1] - b[1], c[1] - d[1])

  def det(a, b):
      return a[0] * b[1] - a[1] * b[0]

  div = det(xdiff, ydiff)
  if div == 0:
     raise Exception('lines do not intersect')

  d = (det(a,b), det(c,d))
  x = det(d, xdiff) / float(div)
  y = det(d, ydiff) / float(div)
  return [x, y]

def pointDistance( a, b):
  return ( (float(b[0]) - float(a[0]))**2 + (float(b[1]) - float(a[1]))**2 ) ** 0.5

def lerp(t,a,b):
  return [int((1-t)*a[0] + t*b[0]), int((1-t)*a[1] + t*b[1])]

def normalizedTunniPoint(a,b):
  return [max(a[0],b[0]),max(a[1],b[1])]

def tension(bez):
  tunniP = lineLineIntersection( *bez )
  percentageP1P2 = pointDistance( bez[0], bez[1] ) / pointDistance( bez[0], tunniP )
  percentageP3P4 = pointDistance( bez[3], bez[2] ) / pointDistance( bez[3], tunniP )
  return ( percentageP1P2 + percentageP3P4 ) / 2

def curveWithTension(start, end, tension):
  return [start,
    lerp(tension, start, normalizedTunniPoint(start, end)),
    lerp(tension, end, normalizedTunniPoint(start, end)),
  end]

# Glyphs stuff
# def arrayToGSPath(bez):
#   p = GSPath.new()
#   nodes = map(lambda f: GSNode(NSMakePoint(f[0],f[1]),OFFCURVE), bez)
#   nodes[0].type = LINE
#   nodes[3].type = CURVE
#   p.nodes = nodes
#   p.closed = False
#   return p

# def segToArray(s):
#   return map(lambda f: [f.x,f.y], s)

# Now the offsetting code

def findBeta(x,a,s,e,dStart,dEnd):
  i = 0
  b = a
  x1,y1 = s[0],s[1]
  x2,y2 = e[0],e[1]
  while i < 5:
    i = i + 1
    newtonstep = ((2867*x*x1)/30030 + (270*a*x*x1)/1001 + (207*a**2*x*x1)/1430 + (27*a**3*x*x1)/1001 - (5*dEnd**2*x*x1)/42 - (2*a*dEnd**2*x*x1)/35 - (17*dEnd*dStart*x*x1)/105 - (a*dEnd*dStart*x*x1)/7 - (19*dStart**2*x*x1)/210 - (a*dStart**2*x*x1)/7 + (191*x**3*x1)/1430 + (804*a*x**3*x1)/5005 + (243*a**2*x**3*x1)/2002 + (36*a**3*x**3*x1)/715 - (262*x1**2)/715 - (111*a*x1**2)/715 - (75*a**2*x1**2)/2002 + (24*b*x1**2)/143 + (69*a*b*x1**2)/715 + (27*a**2*b*x1**2)/1001 + (17*dEnd**2*x1**2)/210 - (2*b*dEnd**2*x1**2)/35 + (5*dEnd*dStart*x1**2)/21 - (b*dEnd*dStart*x1**2)/7 + (13*dStart**2*x1**2)/42 - (b*dStart**2*x1**2)/7 - (1069*x**2*x1**2)/5005 - (1824*a*x**2*x1**2)/5005 - (189*a**2*x**2*x1**2)/715 + (804*b*x**2*x1**2)/5005 + (243*a*b*x**2*x1**2)/1001 + (108*a**2*b*x**2*x1**2)/715 + (2867*x*x1**3)/10010 + (72*a*x*x1**3)/143 - (1824*b*x*x1**3)/5005 - (378*a*b*x*x1**3)/715 + (243*b**2*x*x1**3)/2002 + (108*a*b**2*x*x1**3)/715 - (262*x1**4)/715 + (72*b*x1**4)/143 - (189*b**2*x1**4)/715 + (36*b**3*x1**4)/715 - (2867*x*x2)/30030 - (270*a*x*x2)/1001 - (207*a**2*x*x2)/1430 - (27*a**3*x*x2)/1001 + (5*dEnd**2*x*x2)/42 + (2*a*dEnd**2*x*x2)/35 + (17*dEnd*dStart*x*x2)/105 + (a*dEnd*dStart*x*x2)/7 + (19*dStart**2*x*x2)/210 + (a*dStart**2*x*x2)/7 - (191*x**3*x2)/1430 - (804*a*x**3*x2)/5005 - (243*a**2*x**3*x2)/2002 - (36*a**3*x**3*x2)/715 + (8137*x1*x2)/30030 + (267*a*x1*x2)/5005 - (54*a**2*x1*x2)/5005 - (48*b*x1*x2)/143 - (138*a*b*x1*x2)/715 - (54*a**2*b*x1*x2)/1001 + (4*dEnd**2*x1*x2)/105 + (4*b*dEnd**2*x1*x2)/35 - (8*dEnd*dStart*x1*x2)/105 + (2*b*dEnd*dStart*x1*x2)/7 - (23*dStart**2*x1*x2)/105 + (2*b*dStart**2*x1*x2)/7 - (1873*x**2*x1*x2)/10010 + (216*a*x**2*x1*x2)/5005 + (1431*a**2*x**2*x1*x2)/10010 - (1608*b*x**2*x1*x2)/5005 - (486*a*b*x**2*x1*x2)/1001 - (216*a**2*b*x**2*x1*x2)/715 + (1409*x*x1**2*x2)/10010 - (696*a*x*x1**2*x2)/5005 + (408*b*x*x1**2*x2)/1001 + (4077*a*b*x*x1**2*x2)/5005 - (729*b**2*x*x1**2*x2)/2002 - (324*a*b**2*x*x1**2*x2)/715 + (801*x1**3*x2)/10010 - (3216*b*x1**3*x2)/5005 + (6723*b**2*x1**3*x2)/10010 - (144*b**3*x1**3*x2)/715 + (2867*x2**2)/30030 + (102*a*x2**2)/1001 + (69*a**2*x2**2)/1430 + (24*b*x2**2)/143 + (69*a*b*x2**2)/715 + (27*a**2*b*x2**2)/1001 - (5*dEnd**2*x2**2)/42 - (2*b*dEnd**2*x2**2)/35 - (17*dEnd*dStart*x2**2)/105 - (b*dEnd*dStart*x2**2)/7 - (19*dStart**2*x2**2)/210 - (b*dStart**2*x2**2)/7 + (573*x**2*x2**2)/1430 + (1608*a*x**2*x2**2)/5005 + (243*a**2*x**2*x2**2)/2002 + (804*b*x**2*x2**2)/5005 + (243*a*b*x**2*x2**2)/1001 + (108*a**2*b*x**2*x2**2)/715 - (53*x*x1*x2**2)/2002 - (204*a*x*x1*x2**2)/1001 + (1392*b*x*x1*x2**2)/5005 - (216*a*b*x*x1*x2**2)/5005 + (729*b**2*x*x1*x2**2)/2002 + (324*a*b**2*x*x1*x2**2)/715 + (729*x1**2*x2**2)/10010 - (324*b*x1**2*x2**2)/5005 - (4293*b**2*x1**2*x2**2)/10010 + (216*b**3*x1**2*x2**2)/715 - (573*x*x2**3)/1430 - (804*a*x*x2**3)/5005 - (1608*b*x*x2**3)/5005 - (243*a*b*x*x2**3)/1001 - (243*b**2*x*x2**3)/2002 - (108*a*b**2*x*x2**3)/715 + (801*x1*x2**3)/10010 + (216*b*x1*x2**3)/5005 - (999*b**2*x1*x2**3)/10010 - (144*b**3*x1*x2**3)/715 + (191*x2**4)/1430 + (804*b*x2**4)/5005 + (243*b**2*x2**4)/2002 + (36*b**3*x2**4)/715 - (191*y1)/1430 - (804*a*y1)/5005 - (243*a**2*y1)/2002 - (36*a**3*y1)/715 + (19*dEnd**2*y1)/210 + (a*dEnd**2*y1)/7 + (17*dEnd*dStart*y1)/105 + (a*dEnd*dStart*y1)/7 + (5*dStart**2*y1)/42 + (2*a*dStart**2*y1)/35 - (2867*x**2*y1)/30030 - (270*a*x**2*y1)/1001 - (207*a**2*x**2*y1)/1430 - (27*a**3*x**2*y1)/1001 - (243*x*x1*y1)/5005 - (23*a*x*x1*y1)/143 - (108*a**2*x*x1*y1)/5005 - (204*b*x*x1*y1)/1001 - (276*a*b*x*x1*y1)/715 - (108*a**2*b*x*x1*y1)/1001 + (857*x1**2*y1)/1430 + (509*a*x1**2*y1)/5005 - (18*b*x1**2*y1)/715 + (267*a*b*x1**2*y1)/5005 - (207*b**2*x1**2*y1)/1430 - (81*a*b**2*x1**2*y1)/1001 + (5734*x*x2*y1)/15015 + (876*a*x*x2*y1)/1001 + (138*a**2*x*x2*y1)/715 + (204*b*x*x2*y1)/1001 + (276*a*b*x*x2*y1)/715 + (108*a**2*b*x*x2*y1)/1001 - (685*x1*x2*y1)/1001 - (25*a*x1*x2*y1)/143 + (2826*b*x1*x2*y1)/5005 + (1182*a*b*x1*x2*y1)/5005 + (207*b**2*x1*x2*y1)/715 + (162*a*b**2*x1*x2*y1)/1001 - (2867*x2**2*y1)/10010 - (270*a*x2**2*y1)/1001 - (540*b*x2**2*y1)/1001 - (207*a*b*x2**2*y1)/715 - (207*b**2*x2**2*y1)/1430 - (81*a*b**2*x2**2*y1)/1001 + (573*y1**2)/1430 + (1608*a*y1**2)/5005 + (243*a**2*y1**2)/2002 + (804*b*y1**2)/5005 + (243*a*b*y1**2)/1001 + (108*a**2*b*y1**2)/715 - (19*dEnd**2*y1**2)/210 - (b*dEnd**2*y1**2)/7 - (17*dEnd*dStart*y1**2)/105 - (b*dEnd*dStart*y1**2)/7 - (5*dStart**2*y1**2)/42 - (2*b*dStart**2*y1**2)/35 + (2867*x**2*y1**2)/30030 + (102*a*x**2*y1**2)/1001 + (69*a**2*x**2*y1**2)/1430 + (24*b*x**2*y1**2)/143 + (69*a*b*x**2*y1**2)/715 + (27*a**2*b*x**2*y1**2)/1001 - (1409*x*x1*y1**2)/30030 + (9*a*x*x1*y1**2)/715 + (412*b*x*x1*y1**2)/5005 + (591*a*b*x*x1*y1**2)/5005 + (207*b**2*x*x1*y1**2)/1430 + (81*a*b**2*x*x1*y1**2)/1001 - (333*x1**2*y1**2)/1430 - (446*b*x1**2*y1**2)/5005 + (162*b**2*x1**2*y1**2)/5005 + (54*b**3*x1**2*y1**2)/1001 - (2867*x*x2*y1**2)/10010 - (270*a*x*x2*y1**2)/1001 - (540*b*x*x2*y1**2)/1001 - (207*a*b*x*x2*y1**2)/715 - (207*b**2*x*x2*y1**2)/1430 - (81*a*b**2*x*x2*y1**2)/1001 + (12413*x1*x2*y1**2)/30030 - (538*b*x1*x2*y1**2)/5005 - (1611*b**2*x1*x2*y1**2)/5005 - (108*b**3*x1*x2*y1**2)/1001 + (2867*x2**2*y1**2)/15015 + (540*b*x2**2*y1**2)/1001 + (207*b**2*x2**2*y1**2)/715 + (54*b**3*x2**2*y1**2)/1001 - (573*y1**3)/1430 - (804*a*y1**3)/5005 - (1608*b*y1**3)/5005 - (243*a*b*y1**3)/1001 - (243*b**2*y1**3)/2002 - (108*a*b**2*y1**3)/715 + (191*y1**4)/1430 + (804*b*y1**4)/5005 + (243*b**2*y1**4)/2002 + (36*b**3*y1**4)/715 + (191*y2)/1430 + (804*a*y2)/5005 + (243*a**2*y2)/2002 + (36*a**3*y2)/715 - (19*dEnd**2*y2)/210 - (a*dEnd**2*y2)/7 - (17*dEnd*dStart*y2)/105 - (a*dEnd*dStart*y2)/7 - (5*dStart**2*y2)/42 - (2*a*dStart**2*y2)/35 + (2867*x**2*y2)/30030 + (270*a*x**2*y2)/1001 + (207*a**2*x**2*y2)/1430 + (27*a**3*x**2*y2)/1001 - (4276*x*x1*y2)/15015 - (554*a*x*x1*y2)/1001 - (150*a**2*x*x1*y2)/1001 + (204*b*x*x1*y2)/1001 + (276*a*b*x*x1*y2)/715 + (108*a**2*b*x*x1*y2)/1001 + (1949*x1**2*y2)/6006 + (778*a*x1**2*y2)/5005 - (2162*b*x1**2*y2)/5005 - (225*a*b*x1**2*y2)/1001 + (207*b**2*x1**2*y2)/1430 + (81*a*b**2*x1**2*y2)/1001 - (243*x*x2*y2)/5005 - (23*a*x*x2*y2)/143 - (108*a**2*x*x2*y2)/5005 - (204*b*x*x2*y2)/1001 - (276*a*b*x*x2*y2)/715 - (108*a**2*b*x*x2*y2)/1001 + (1409*x1*x2*y2)/15015 + (25*a*x1*x2*y2)/143 + (50*b*x1*x2*y2)/143 + (534*a*b*x1*x2*y2)/5005 - (207*b**2*x1*x2*y2)/715 - (162*a*b**2*x1*x2*y2)/1001 - (1409*x2**2*y2)/30030 + (9*a*x2**2*y2)/715 + (412*b*x2**2*y2)/5005 + (591*a*b*x2**2*y2)/5005 + (207*b**2*x2**2*y2)/1430 + (81*a*b**2*x2**2*y2)/1001 - (1873*y1*y2)/10010 + (216*a*y1*y2)/5005 + (1431*a**2*y1*y2)/10010 - (1608*b*y1*y2)/5005 - (486*a*b*y1*y2)/1001 - (216*a**2*b*y1*y2)/715 - (23*dEnd**2*y1*y2)/105 + (2*b*dEnd**2*y1*y2)/7 - (8*dEnd*dStart*y1*y2)/105 + (2*b*dEnd*dStart*y1*y2)/7 + (4*dStart**2*y1*y2)/105 + (4*b*dStart**2*y1*y2)/35 + (8137*x**2*y1*y2)/30030 + (267*a*x**2*y1*y2)/5005 - (54*a**2*x**2*y1*y2)/5005 - (48*b*x**2*y1*y2)/143 - (138*a*b*x**2*y1*y2)/715 - (54*a**2*b*x**2*y1*y2)/1001 + (1409*x*x1*y1*y2)/15015 + (25*a*x*x1*y1*y2)/143 + (50*b*x*x1*y1*y2)/143 + (534*a*b*x*x1*y1*y2)/5005 - (207*b**2*x*x1*y1*y2)/715 - (162*a*b**2*x*x1*y1*y2)/1001 - (7607*x1**2*y1*y2)/30030 + (606*b*x1**2*y1*y2)/5005 + (963*b**2*x1**2*y1*y2)/5005 - (108*b**3*x1**2*y1*y2)/1001 - (685*x*x2*y1*y2)/1001 - (25*a*x*x2*y1*y2)/143 + (2826*b*x*x2*y1*y2)/5005 + (1182*a*b*x*x2*y1*y2)/5005 + (207*b**2*x*x2*y1*y2)/715 + (162*a*b**2*x*x2*y1*y2)/1001 + (486*x1*x2*y1*y2)/5005 - (100*b*x1*x2*y1*y2)/143 + (648*b**2*x1*x2*y1*y2)/5005 + (216*b**3*x1*x2*y1*y2)/1001 + (12413*x2**2*y1*y2)/30030 - (538*b*x2**2*y1*y2)/5005 - (1611*b**2*x2**2*y1*y2)/5005 - (108*b**3*x2**2*y1*y2)/1001 - (53*y1**2*y2)/2002 - (204*a*y1**2*y2)/1001 + (1392*b*y1**2*y2)/5005 - (216*a*b*y1**2*y2)/5005 + (729*b**2*y1**2*y2)/2002 + (324*a*b**2*y1**2*y2)/715 + (801*y1**3*y2)/10010 + (216*b*y1**3*y2)/5005 - (999*b**2*y1**3*y2)/10010 - (144*b**3*y1**3*y2)/715 - (1069*y2**2)/5005 - (1824*a*y2**2)/5005 - (189*a**2*y2**2)/715 + (804*b*y2**2)/5005 + (243*a*b*y2**2)/1001 + (108*a**2*b*y2**2)/715 + (13*dEnd**2*y2**2)/42 - (b*dEnd**2*y2**2)/7 + (5*dEnd*dStart*y2**2)/21 - (b*dEnd*dStart*y2**2)/7 + (17*dStart**2*y2**2)/210 - (2*b*dStart**2*y2**2)/35 - (262*x**2*y2**2)/715 - (111*a*x**2*y2**2)/715 - (75*a**2*x**2*y2**2)/2002 + (24*b*x**2*y2**2)/143 + (69*a*b*x**2*y2**2)/715 + (27*a**2*b*x**2*y2**2)/1001 + (1949*x*x1*y2**2)/6006 + (778*a*x*x1*y2**2)/5005 - (2162*b*x*x1*y2**2)/5005 - (225*a*b*x*x1*y2**2)/1001 + (207*b**2*x*x1*y2**2)/1430 + (81*a*b**2*x*x1*y2**2)/1001 - (2138*x1**2*y2**2)/15015 + (1556*b*x1**2*y2**2)/5005 - (225*b**2*x1**2*y2**2)/1001 + (54*b**3*x1**2*y2**2)/1001 + (857*x*x2*y2**2)/1430 + (509*a*x*x2*y2**2)/5005 - (18*b*x*x2*y2**2)/715 + (267*a*b*x*x2*y2**2)/5005 - (207*b**2*x*x2*y2**2)/1430 - (81*a*b**2*x*x2*y2**2)/1001 - (7607*x1*x2*y2**2)/30030 + (606*b*x1*x2*y2**2)/5005 + (963*b**2*x1*x2*y2**2)/5005 - (108*b**3*x1*x2*y2**2)/1001 - (333*x2**2*y2**2)/1430 - (446*b*x2**2*y2**2)/5005 + (162*b**2*x2**2*y2**2)/5005 + (54*b**3*x2**2*y2**2)/1001 + (1409*y1*y2**2)/10010 - (696*a*y1*y2**2)/5005 + (408*b*y1*y2**2)/1001 + (4077*a*b*y1*y2**2)/5005 - (729*b**2*y1*y2**2)/2002 - (324*a*b**2*y1*y2**2)/715 + (729*y1**2*y2**2)/10010 - (324*b*y1**2*y2**2)/5005 - (4293*b**2*y1**2*y2**2)/10010 + (216*b**3*y1**2*y2**2)/715 + (2867*y2**3)/10010 + (72*a*y2**3)/143 - (1824*b*y2**3)/5005 - (378*a*b*y2**3)/715 + (243*b**2*y2**3)/2002 + (108*a*b**2*y2**3)/715 + (801*y1*y2**3)/10010 - (3216*b*y1*y2**3)/5005 + (6723*b**2*y1*y2**3)/10010 - (144*b**3*y1*y2**3)/715 - (262*y2**4)/715 + (72*b*y2**4)/143 - (189*b**2*y2**4)/715 + (36*b**3*y2**4)/715)/((24*x1**2)/143 + (69*a*x1**2)/715 + (27*a**2*x1**2)/1001 - (2*dEnd**2*x1**2)/35 - (dEnd*dStart*x1**2)/7 - (dStart**2*x1**2)/7 + (804*x**2*x1**2)/5005 + (243*a*x**2*x1**2)/1001 + (108*a**2*x**2*x1**2)/715 - (1824*x*x1**3)/5005 - (378*a*x*x1**3)/715 + (243*b*x*x1**3)/1001 + (216*a*b*x*x1**3)/715 + (72*x1**4)/143 - (378*b*x1**4)/715 + (108*b**2*x1**4)/715 - (48*x1*x2)/143 - (138*a*x1*x2)/715 - (54*a**2*x1*x2)/1001 + (4*dEnd**2*x1*x2)/35 + (2*dEnd*dStart*x1*x2)/7 + (2*dStart**2*x1*x2)/7 - (1608*x**2*x1*x2)/5005 - (486*a*x**2*x1*x2)/1001 - (216*a**2*x**2*x1*x2)/715 + (408*x*x1**2*x2)/1001 + (4077*a*x*x1**2*x2)/5005 - (729*b*x*x1**2*x2)/1001 - (648*a*b*x*x1**2*x2)/715 - (3216*x1**3*x2)/5005 + (6723*b*x1**3*x2)/5005 - (432*b**2*x1**3*x2)/715 + (24*x2**2)/143 + (69*a*x2**2)/715 + (27*a**2*x2**2)/1001 - (2*dEnd**2*x2**2)/35 - (dEnd*dStart*x2**2)/7 - (dStart**2*x2**2)/7 + (804*x**2*x2**2)/5005 + (243*a*x**2*x2**2)/1001 + (108*a**2*x**2*x2**2)/715 + (1392*x*x1*x2**2)/5005 - (216*a*x*x1*x2**2)/5005 + (729*b*x*x1*x2**2)/1001 + (648*a*b*x*x1*x2**2)/715 - (324*x1**2*x2**2)/5005 - (4293*b*x1**2*x2**2)/5005 + (648*b**2*x1**2*x2**2)/715 - (1608*x*x2**3)/5005 - (243*a*x*x2**3)/1001 - (243*b*x*x2**3)/1001 - (216*a*b*x*x2**3)/715 + (216*x1*x2**3)/5005 - (999*b*x1*x2**3)/5005 - (432*b**2*x1*x2**3)/715 + (804*x2**4)/5005 + (243*b*x2**4)/1001 + (108*b**2*x2**4)/715 - (204*x*x1*y1)/1001 - (276*a*x*x1*y1)/715 - (108*a**2*x*x1*y1)/1001 - (18*x1**2*y1)/715 + (267*a*x1**2*y1)/5005 - (207*b*x1**2*y1)/715 - (162*a*b*x1**2*y1)/1001 + (204*x*x2*y1)/1001 + (276*a*x*x2*y1)/715 + (108*a**2*x*x2*y1)/1001 + (2826*x1*x2*y1)/5005 + (1182*a*x1*x2*y1)/5005 + (414*b*x1*x2*y1)/715 + (324*a*b*x1*x2*y1)/1001 - (540*x2**2*y1)/1001 - (207*a*x2**2*y1)/715 - (207*b*x2**2*y1)/715 - (162*a*b*x2**2*y1)/1001 + (804*y1**2)/5005 + (243*a*y1**2)/1001 + (108*a**2*y1**2)/715 - (dEnd**2*y1**2)/7 - (dEnd*dStart*y1**2)/7 - (2*dStart**2*y1**2)/35 + (24*x**2*y1**2)/143 + (69*a*x**2*y1**2)/715 + (27*a**2*x**2*y1**2)/1001 + (412*x*x1*y1**2)/5005 + (591*a*x*x1*y1**2)/5005 + (207*b*x*x1*y1**2)/715 + (162*a*b*x*x1*y1**2)/1001 - (446*x1**2*y1**2)/5005 + (324*b*x1**2*y1**2)/5005 + (162*b**2*x1**2*y1**2)/1001 - (540*x*x2*y1**2)/1001 - (207*a*x*x2*y1**2)/715 - (207*b*x*x2*y1**2)/715 - (162*a*b*x*x2*y1**2)/1001 - (538*x1*x2*y1**2)/5005 - (3222*b*x1*x2*y1**2)/5005 - (324*b**2*x1*x2*y1**2)/1001 + (540*x2**2*y1**2)/1001 + (414*b*x2**2*y1**2)/715 + (162*b**2*x2**2*y1**2)/1001 - (1608*y1**3)/5005 - (243*a*y1**3)/1001 - (243*b*y1**3)/1001 - (216*a*b*y1**3)/715 + (804*y1**4)/5005 + (243*b*y1**4)/1001 + (108*b**2*y1**4)/715 + (204*x*x1*y2)/1001 + (276*a*x*x1*y2)/715 + (108*a**2*x*x1*y2)/1001 - (2162*x1**2*y2)/5005 - (225*a*x1**2*y2)/1001 + (207*b*x1**2*y2)/715 + (162*a*b*x1**2*y2)/1001 - (204*x*x2*y2)/1001 - (276*a*x*x2*y2)/715 - (108*a**2*x*x2*y2)/1001 + (50*x1*x2*y2)/143 + (534*a*x1*x2*y2)/5005 - (414*b*x1*x2*y2)/715 - (324*a*b*x1*x2*y2)/1001 + (412*x2**2*y2)/5005 + (591*a*x2**2*y2)/5005 + (207*b*x2**2*y2)/715 + (162*a*b*x2**2*y2)/1001 - (1608*y1*y2)/5005 - (486*a*y1*y2)/1001 - (216*a**2*y1*y2)/715 + (2*dEnd**2*y1*y2)/7 + (2*dEnd*dStart*y1*y2)/7 + (4*dStart**2*y1*y2)/35 - (48*x**2*y1*y2)/143 - (138*a*x**2*y1*y2)/715 - (54*a**2*x**2*y1*y2)/1001 + (50*x*x1*y1*y2)/143 + (534*a*x*x1*y1*y2)/5005 - (414*b*x*x1*y1*y2)/715 - (324*a*b*x*x1*y1*y2)/1001 + (606*x1**2*y1*y2)/5005 + (1926*b*x1**2*y1*y2)/5005 - (324*b**2*x1**2*y1*y2)/1001 + (2826*x*x2*y1*y2)/5005 + (1182*a*x*x2*y1*y2)/5005 + (414*b*x*x2*y1*y2)/715 + (324*a*b*x*x2*y1*y2)/1001 - (100*x1*x2*y1*y2)/143 + (1296*b*x1*x2*y1*y2)/5005 + (648*b**2*x1*x2*y1*y2)/1001 - (538*x2**2*y1*y2)/5005 - (3222*b*x2**2*y1*y2)/5005 - (324*b**2*x2**2*y1*y2)/1001 + (1392*y1**2*y2)/5005 - (216*a*y1**2*y2)/5005 + (729*b*y1**2*y2)/1001 + (648*a*b*y1**2*y2)/715 + (216*y1**3*y2)/5005 - (999*b*y1**3*y2)/5005 - (432*b**2*y1**3*y2)/715 + (804*y2**2)/5005 + (243*a*y2**2)/1001 + (108*a**2*y2**2)/715 - (dEnd**2*y2**2)/7 - (dEnd*dStart*y2**2)/7 - (2*dStart**2*y2**2)/35 + (24*x**2*y2**2)/143 + (69*a*x**2*y2**2)/715 + (27*a**2*x**2*y2**2)/1001 - (2162*x*x1*y2**2)/5005 - (225*a*x*x1*y2**2)/1001 + (207*b*x*x1*y2**2)/715 + (162*a*b*x*x1*y2**2)/1001 + (1556*x1**2*y2**2)/5005 - (450*b*x1**2*y2**2)/1001 + (162*b**2*x1**2*y2**2)/1001 - (18*x*x2*y2**2)/715 + (267*a*x*x2*y2**2)/5005 - (207*b*x*x2*y2**2)/715 - (162*a*b*x*x2*y2**2)/1001 + (606*x1*x2*y2**2)/5005 + (1926*b*x1*x2*y2**2)/5005 - (324*b**2*x1*x2*y2**2)/1001 - (446*x2**2*y2**2)/5005 + (324*b*x2**2*y2**2)/5005 + (162*b**2*x2**2*y2**2)/1001 + (408*y1*y2**2)/1001 + (4077*a*y1*y2**2)/5005 - (729*b*y1*y2**2)/1001 - (648*a*b*y1*y2**2)/715 - (324*y1**2*y2**2)/5005 - (4293*b*y1**2*y2**2)/5005 + (648*b**2*y1**2*y2**2)/715 - (1824*y2**3)/5005 - (378*a*y2**3)/715 + (243*b*y2**3)/1001 + (216*a*b*y2**3)/715 - (3216*y1*y2**3)/5005 + (6723*b*y1*y2**3)/5005 - (432*b**2*y1*y2**3)/715 + (72*y2**4)/143 - (378*b*y2**4)/715 + (108*b**2*y2**4)/715)
    b = b - newtonstep
  return b

# And this is the main routine
def offset(bez, sAngle, eAngle, d1, d2=None):
  if not d2:
    d2 = d1
  if bez[0][0] > bez[3][0]:
    bez = list(reversed(bez))
  tr = unitize(*bez)
  s = [ bez[0][0] + d1 * cos(sAngle), bez[0][1] + d1 * sin(sAngle) ]
  e = [ bez[3][0] + d2 * cos(eAngle), bez[3][1] + d2 * sin(eAngle) ]
  print(s,e)
  bez2 = applyTransform(bez,tr)
  alpha = tension(bez)
  scaledD1 = d1 / tr["scale"]
  scaledD2 = d2 / tr["scale"]
  scaledS = apply1(s,tr)
  scaledE = apply1(e,tr)
  print(scaledS, scaledE)

  beta = findBeta(bez2[3][0], alpha, scaledS, scaledE, scaledD1, scaledD2)
  if beta < 0 or beta > 1:
    raise ValueError
  offsetCurve = curveWithTension(
    s,
    e,
    beta
  )
  return offsetCurve

# p = Glyphs.font.selectedLayers[0].paths[0]
# arr = segToArray(p.segments[0])
# dStart = 120
# dEnd   = 60
# path2 = arrayToGSPath(offset(arr, 0, radians(90), dStart, dEnd))
# Glyphs.font.selectedLayers[0].paths.append(path2)