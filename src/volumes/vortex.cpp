// volumes/volumegrid.cpp*
#include "stdafx.h"
#include "volumes/vortex.h"
#include "paramset.h"

float fmap(float x, float omin, float omax, float nmin, float nmax){
    x = (x-omin) / (omax-omin);
    return nmin + x * (nmax - nmin);
}

// VolumeVortex Method Definitions
float VolumeVortex::Density(const Point &Pobj) const {
    if (!extent.Inside(Pobj)) return 0;
	if (Pobj.y < killbelow) return 0;

    Vector dpdx, dpdy;

    float cx = (extent.pMin.x + extent.pMax.x) / 2.f;
    float cy = (extent.pMin.y + extent.pMax.y) / 2.f;
    float cz = (extent.pMin.z + extent.pMax.z) / 2.f;

    float ox = Pobj.x - cx;
    float oy = Pobj.y - cy;
    float oz = Pobj.z - cz;

    float rx = extent.pMax.x - extent.pMin.x;
    float ry = extent.pMax.y - extent.pMin.y;
    float rz = extent.pMax.z - extent.pMin.z;

    float h = Pobj.y - extent.pMin.y;
    float fraction_from_base = fmap(h, 0, ry, 0, 1);

    // float oa = FBm(Pobj, dpdx, dpdy, 1.f, 4.f);
    // ox += sin(fraction_from_base * 3.2);
    // oz += cos(fraction_from_base * 3.2);
    float dist_from_axis = sqrt(ox*ox + oz*oz);

    float radius = pow(2, fraction_from_base * 2 - 2) - 0.2;
    radius += (FBm(Pobj, dpdx, dpdy, 0.2f, 4.f) / 10.f) * fraction_from_base;

    float lower_limit = fmap(dist_from_axis, 0, radius, 0.f, 1.f);

    lower_limit = b / (1.f + exp(-s * (lower_limit - p))) + a;
    lower_limit -= (1.f - fraction_from_base);
    if (fraction_from_base > 0.8){
        lower_limit += (fraction_from_base - 0.8f) * 3;
    }

	Point ip(ox + step, oy, oz);
    return Clamp(Turbulence(ip, dpdx, dpdy, 1.f, 6) - lower_limit, 0.f, 1.f) ;
}


VolumeVortex *CreateVortexVolumeRegion(const Transform &volume2world,
        const ParamSet &params) {
    // Initialize common volume region parameters
    Spectrum sigma_a = params.FindOneSpectrum("sigma_a", 0.);
    Spectrum sigma_s = params.FindOneSpectrum("sigma_s", 0.);
    float g = params.FindOneFloat("g", 0.);
    Spectrum Le = params.FindOneSpectrum("Le", 0.);
    Point p0 = params.FindOnePoint("p0", Point(0,0,0));
    Point p1 = params.FindOnePoint("p1", Point(1,1,1));

	float killbelow = params.FindOneFloat("killbelow", 0.);
	float step = params.FindOneFloat("step", 0.);

	float p = params.FindOneFloat("p", 1.8f);
	float s = params.FindOneFloat("s", 1.5f);
	float b = params.FindOneFloat("b", 6.f);
	float a = params.FindOneFloat("a", 0.75f);

	return new VolumeVortex(sigma_a, sigma_s, g, Le, BBox(p0, p1), killbelow, step, p, s, b, a, volume2world);
}


