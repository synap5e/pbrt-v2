#if defined(_MSC_VER)
#pragma once
#endif

#ifndef PBRT_VOLUMES_VORTEX_H
#define PBRT_VOLUMES_VORTEX_H

// volumes/vortex.h*
#include "volume.h"

// VolumeVortex Declarations
class VolumeVortex : public DensityRegion {
public:
    // VolumeVortex Public Methods
    VolumeVortex(const Spectrum &sa,
                 const Spectrum &ss,
                 float gg,
                 const Spectrum &emit,
                 const BBox &e,
				 const float killbelow,
				 const float step,
				 const float p,
				 const float s,
				 const float b,
				 const float a,
				 const Transform &v2w)
				 : DensityRegion(sa, ss, gg, emit, v2w), extent(e), killbelow(killbelow), step(step), p(p), s(s), b(b), a(a){
    }
    ~VolumeVortex() { }
    BBox WorldBound() const { return Inverse(WorldToVolume)(extent); }
    bool IntersectP(const Ray &r, float *t0, float *t1) const {
        Ray ray = WorldToVolume(r);
        return extent.IntersectP(ray, t0, t1);
    }
    float Density(const Point &Pobj) const;
private:
    // VolumeVortex Private Data
    const BBox extent;
	const float killbelow;
	const float step;

	const float p;
	const float s;
	const float b;
	const float a;
};


VolumeVortex *CreateVortexVolumeRegion(const Transform &volume2world, const ParamSet &params);

#endif // PBRT_VOLUMES_VORTEX_H
