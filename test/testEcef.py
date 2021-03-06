
# -*- coding: utf-8 -*-

u'''Test Ecef conversions.
'''

__all__ = ('Tests',)
__version__ = '20.04.04'

from base import TestsBase

from pygeodesy import Datums, EcefCartesian, EcefKarney, EcefMatrix, EcefVeness, EcefYou, \
                      Ellipsoids, fstr, latDMS, LatLon_, lonDMS, nvector, parse3llh

from math import radians


class Tests(TestsBase):

    def testEcef(self, Ecef):

        self.test(Ecef.__name__, '...', '...', nl=1)

        Karney = Ecef is EcefKarney

        g = Ecef(Datums.WGS84, name='Test')
        self.test('name', g.name, 'Test')

        t = g.toStr2()
        self.test('toStr', t, g.classname, known=True)

        t = Ecef(g.a, g.f, name=g.name)  # coverage
        self.test('a, f', t, t.classname, known=True)

        self.testCopy(g)

        # <https://GeographicLib.SourceForge.io/html/classGeographicLib_1_1Geocentric.html>
        t = g.forward(27.99, 86.93, 8820)  # Mt Everest
        self.test('forward', fstr(t[3:6], prec=2), '27.99, 86.93, 8820.0')
        self.test('forward', fstr(t[0:3], prec=1), '302271.4, 5635928.4, 2979666.1')
        self.test('name', t.name, 'Test')

        t = g.reverse(302271.4, 5635928.4, 2979666.1)
        self.test('reverse', fstr(t[0:3], prec=1), '302271.4, 5635928.4, 2979666.1')
        self.test('reverse', fstr(t[3:6], prec=2), '27.99, 86.93, 8820.01')
        self.test('case', t.C, 2 if Karney else 1)
        self.test('name', t.name, 'Test')

        # <https://GeographicLib.SourceForge.io/html/classGeographicLib_1_1Geocentric.html>
        t = g.reverse(302e3, 5636e3, 2980e3)
        self.test('reverse', fstr(t[0:3], prec=1), '302000.0, 5636000.0, 2980000.0')
        self.test('reverse', fstr(t[3:6], prec=2), '27.99, 86.93, 9027.03')  # 8820.0
        self.test('case', t.C, 2 if Karney else 1)

        t = g.forward(27.99, 86.93, 8820.0)
        self.test('forward', fstr(t[3:6], prec=2), '27.99, 86.93, 8820.0')
        self.test('forward', fstr(t[0:3], prec=2), '302271.43, 5635928.37, 2979666.13')

        # <https://GeographicLib.SourceForge.io/html/CartConvert.1.html>
        t = g.forward(33.3, 44.4, 6000)
        self.test('forward', fstr(t[3:6], prec=2), '33.3, 44.4, 6000.0')
        self.test('forward', fstr(t[0:3], prec=2), '3816209.6, 3737108.55, 3485109.57')

        t = g.reverse(3816209.6, 3737108.55, 3485109.57)
        self.test('reverse', fstr(t[0:3], prec=2), '3816209.6, 3737108.55, 3485109.57')
        self.test('reverse', fstr(t[3:6], prec=3), '33.3, 44.4, 5999.996')  # 6000.0
        self.test('case', t.C, 2 if Karney else 1)

        # <https://GeographicLib.SourceForge.io/html/CartConvert.1.html>
        t = g.reverse(30000, 30000, 0)
        self.test('reverse', fstr(t[0:3], prec=1), '30000.0, 30000.0, 0.0')
        self.test('reverse', fstr(t[3:6], prec=3), '6.483, 45.0, -6335709.726', known=not Karney)
        self.test('case', t.C, 3 if Karney else 1)

        t = g.forward(6.483, 45.0, -6335709.726)
        self.test('forward', fstr(t[3:6], prec=3), '6.483, 45.0, -6335709.726')
        self.test('forward', fstr(t[0:3], prec=1), '30000.0, 30000.0, -0.0', known=True)

        # Rey-Jer You <https://www.ResearchGate.net/publication/240359424>
        for i, (x, y, z, h) in enumerate(((-2259148.993, 3912960.837, 4488055.516, 1e3),
                                          (-2259502.546, 3913573.210, 4488762.622, 2e3),
                                          (-2259856.100, 3914185.582, 4489469.729, 3e3),
                                          (-2260209.653, 3914797.955, 4490176.836, 4e3),
                                          (-2262330.973, 3918472.189, 4494419.477, 1e4),
                                          (-2265866.507, 3924595.914, 4501490.544, 2e4),
                                          (-2294150.778, 3973585.709, 4558059.087, 1e5),
                                          (-2541638.152, 4402246.414, 5053033.834, 8e5),
                                          (-2612348.830, 4524720.901, 5194455.190, 1e6))):
            i = '-%d' % (i + 1,)
            r = '45.0, 120.0, %.1f' % (h,)  # Zero and First order columns
            t = g.reverse(x, y, z)
            self.test('reverse' + i, fstr(t[3:6], prec=3), r)
            f = g.forward(t.lat, t.lon, t.height)
            self.test('forward' + i, fstr(f[0:3], prec=1), fstr((x, y, z), prec=1))
            self.test('xyzh' + i, fstr(f.xyzh, prec=1), fstr((x, y, z, h), prec=1))
            f = f.phi, f.lam
            t = radians(t.lat), radians(t.lon)
            self.test('philam' + i, fstr(f, prec=4), fstr(t, prec=4))

        # <https://www.OrdnanceSurvey.co.UK/documents/resources/guide-coordinate-systems-great-britain.pdf> pp 47
        g = Ecef(Ellipsoids.GRS80, name='OS-UK')
        self.test('name', g.name, 'OS-UK')

        t = g.forward(parse3llh('''53°36′43.1653"N, 001°39′51.9920"W, 299.800'''))
        self.test('forward', fstr(t[3:6], prec=8), '53.61199036, -1.66444222, 299.8')
        self.test('forward', fstr(t[0:3], prec=2), '3790644.9, -110149.21, 5111482.97')

        t = g.reverse(3790644.9, -110149.21, 5111482.97)
        self.test('reverse', fstr(t[0:3], prec=2), '3790644.9, -110149.21, 5111482.97')
        self.test('reverse', fstr(t[3:5], prec=8), '53.61199036, -1.66444223')
        self.test('reverse.lat', latDMS(t.lat, prec=4), '53°36′43.1653″N')
        self.test('reverse.lon', lonDMS(t.lon, prec=4), '001°39′51.992″W')
        self.test('reverse.height', fstr(t.height, prec=-3), '299.800')
        self.test('case', t.C, 2 if Karney else 1)

    def testEcefCartesian(self):

        self.test(EcefCartesian.__name__, '...', '...', nl=1)

        # <https://GeographicLib.SourceForge.io/html/CartConvert.1.html>
        c = EcefCartesian(33, 44, 20, name='Test')
        self.test('name', c.name, 'Test')
        t = c.toStr2()
        self.test('toStr', t, c.classname, known=True)

        self.testCopy(c)

        t = c.forward(33.3, 44.4, 6000)
        self.test('forward', fstr(t[3:6], prec=1), '33.3, 44.4, 6000.0')
        self.test('forward', fstr(t[0:3], prec=2), '37288.97, 33374.29, 5783.65')  # 5783.64
        self.test('name', c.name, 'Test')

        t = c.reverse(37288.97, 33374.29, 5783.65)
        self.test('reverse', fstr(t[3:6], prec=2), '33.3, 44.4, 6000.0')
        self.test('name', c.name, 'Test')

        # <https://SourceForge.net/p/geographiclib/code/ci/release/tree/examples/example-LocalCartesian.cpp>
        c.reset(48 + 50 / 60.0, 2 + 20 / 60.0, name='Paris')
        self.test('name', c.name, 'Paris')
        self.test(c.name, fstr((c.lat0, c.lon0, c.height0), prec=3), '48.833, 2.333, 0.0')

        t = c.forward(LatLon_(50.9, 1.8, name='Calais'))
        self.test('forward', fstr(t[3:6], prec=1), '50.9, 1.8, 0.0')
        self.test('forward', fstr(t[0:3], prec=2), '-37518.64, 229949.65, -4260.43')
        self.test('name', t.name, 'Calais')

        t = c.reverse(-37518.64, 229949.65, -4260.43)
        self.test('reverse', fstr(t[3:6], prec=2), '50.9, 1.8, -0.0', know=True)
        self.test('name', t.name, 'Paris')

        t = c.reverse(-38e3, 230e3, -4e3)
        self.test('reverse', fstr(t[0:3], prec=1), '4028834.2, 126130.9, 4926765.2')
        self.test('reverse', fstr(t[3:6], prec=2), '50.9, 1.79, 264.92')

        t = c.forward(50.9, 1.79, 264.92)
        self.test('forward', fstr(t[0:3], prec=1), '-38000.0, 230000.0, -4000.0', known=True)

    def testEcefMatrix(self):

        self.test(EcefMatrix.__name__, '...', '...', nl=1)

        # index order in .multiply
        t = tuple(r * 3 + c for r in range(3) for c in range(3))
        self.test('index', t, '(0, 1, 2, 3, 4, 5, 6, 7, 8)')

        M = EcefMatrix(*t)
        self.test('matrix', fstr(M, prec=0), '0, 1, 2, 3, 4, 5, 6, 7, 8')
        t = M.multiply(M)
        self.test('multiply', fstr(t, prec=0), '45, 54, 63, 54, 66, 78, 63, 78, 93')

        self.testCopy(M)

        I = [0] * 9  # PYCHOK I
        I[0] = I[4] = I[8] = 1
        I = EcefMatrix(*I)  # PYCHOK I
        self.test('matrix', fstr(I, prec=0), '1, 0, 0, 0, 1, 0, 0, 0, 1')
        t = I.multiply(I)
        self.test('multiply', fstr(t, prec=0), '1, 0, 0, 0, 1, 0, 0, 0, 1')

        self.testCopy(I)

    def testLatLonEcef(self, module):

        self.test(module.__name__, 'LatLon', 'LatLon', nl=1)

        ll = module.LatLon(48.833, 2.333, name='Paris')
        t = ll.toEcef()
        self.test('forward', fstr(t[3:6], prec=3), '48.833, 2.333, 0.0')
        self.test('forward', fstr(t[0:3], prec=2), '4202946.8, 171232.47, 4778354.17' if ll.isEllipsoidal
                                              else '4190278.55, 170716.35, 4796058.21')
        self.test('name', t.name, 'Paris')

        e = ll.datum.ecef().reverse(t)
        self.test('reverse', fstr(e[3:6], prec=3), '48.833, 2.333, 0.0')
        self.test('name', e.name, 'Paris')

        ll = e.toLatLon(module.LatLon)
        self.test('toLatLon', repr(ll), 'LatLon(48°49′58.8″N, 002°19′58.8″E, +0.00m)' if ll.isEllipsoidal
                                   else 'LatLon(48°49′58.8″N, 002°19′58.8″E)')
        self.test('name', ll.name, 'Paris')

        t = e.toLatLon(LatLon=None)
        self.test('to4Tuple', t.classname, 'LatLon4Tuple')
        self.test('to4Tuple', repr(t), 'Paris(lat=48.833, lon=2.333, height=0.0, datum=%r)' % (t.datum,))

        t = e.toLatLon(LatLon=None, datum=None)
        self.test('to3Tuple', t.classname, 'LatLon3Tuple')
        self.test('to3Tuple', repr(t), 'Paris(lat=48.833, lon=2.333, height=0.0)')

        v = e.toVector(getattr(module, 'Nvector', nvector.Nvector))  # XXX missing Nvector?
        self.test('toVector', str(v), '(4202946.79528, 171232.46613, 4778354.17)' if ll.isEllipsoidal
                                 else '(4190278.55277, 170716.34863, 4796058.20898)')
        self.test('name', v.name, 'Paris')

        c = e.toCartesian(module.Cartesian)
        self.test('forward', c.toStr(prec=2), '[4202946.8, 171232.47, 4778354.17]' if ll.isEllipsoidal
                                         else '[4190278.55, 170716.35, 4796058.21]')


if __name__ == '__main__':

    from pygeodesy import ellipsoidalKarney, ellipsoidalNvector, ellipsoidalVincenty, \
                          sphericalNvector, sphericalTrigonometry

    t = Tests(__file__, __version__)
    t.testEcef(EcefKarney)
    t.testEcefCartesian()
    t.testEcef(EcefVeness)
    t.testEcef(EcefYou)
    t.testEcefMatrix()
    t.testLatLonEcef(ellipsoidalKarney)
    t.testLatLonEcef(ellipsoidalNvector)
    t.testLatLonEcef(ellipsoidalVincenty)
    t.testLatLonEcef(sphericalNvector)
    t.testLatLonEcef(sphericalTrigonometry)
    t.results()
    t.exit()
