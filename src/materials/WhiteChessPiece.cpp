
/*
    pbrt source code Copyright(c) 1998-2012 Matt Pharr and Greg Humphreys.

    This file is part of pbrt.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:

    - Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    - Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
    IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
    TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
    PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
    HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

 */


// materials/subsurface.cpp*
#include "stdafx.h"
#include "materials/WhiteChessPiece.h"
#include "textures/constant.h"
#include "volume.h"
#include "spectrum.h"
#include "reflection.h"
#include "texture.h"
#include "paramset.h"

// SubsurfaceMaterial Method Definitions
BSDF *WhiteChessPieceMaterial::GetBSDF(const DifferentialGeometry &dgGeom,
        const DifferentialGeometry &dgShading, MemoryArena &arena) const {
    // Allocate _BSDF_, possibly doing bump mapping with _bumpMap_
	// Allocate _BSDF_, possibly doing bump mapping with _bumpMap_
	DifferentialGeometry dgs;
	if (bumpMap)
		Bump(bumpMap, dgGeom, dgShading, &dgs);
	else
		dgs = dgShading;
	BSDF *bsdf = BSDF_ALLOC(arena, BSDF)(dgs, dgGeom.nn);

	Spectrum kd = Kd->Evaluate(dgs).Clamp();
	if (!kd.IsBlack()) {
		BxDF *diff = BSDF_ALLOC(arena, Lambertian)(kd);
		bsdf->Add(diff);
	}

	float e = eta->Evaluate(dgs);
	Spectrum ks = Ks->Evaluate(dgs).Clamp();
	if (!ks.IsBlack()) {
		Fresnel *fresnel = BSDF_ALLOC(arena, FresnelDielectric)(e, 1.f);
		float urough = uroughness->Evaluate(dgs);
		float vrough = vroughness->Evaluate(dgs);
		BxDF *spec = BSDF_ALLOC(arena, Microfacet)(ks, fresnel, BSDF_ALLOC(arena, Anisotropic)(1.f / urough, 1.f / vrough));
		bsdf->Add(spec);
	}

	Spectrum kr =  Kr->Evaluate(dgs).Clamp();
	if (!kr.IsBlack()) {
		Fresnel *fresnel = BSDF_ALLOC(arena, FresnelDielectric)(e, 1.f);
		bsdf->Add(BSDF_ALLOC(arena, SpecularReflection)(kr, fresnel));
	}
	return bsdf;
}

BSSRDF *WhiteChessPieceMaterial::GetBSSRDF(const DifferentialGeometry &dgGeom,
	const DifferentialGeometry &dgShading,
	MemoryArena &arena) const {
	float e = eta->Evaluate(dgShading) * scale;
	float mfp = meanfreepath->Evaluate(dgShading);
	Spectrum kd = Ksss->Evaluate(dgShading).Clamp();
	Spectrum sigma_a, sigma_prime_s;
	SubsurfaceFromDiffuse(kd, mfp, e, &sigma_a, &sigma_prime_s);

	return BSDF_ALLOC(arena, BSSRDF)(sigma_a, sigma_prime_s, e);
}



WhiteChessPieceMaterial *CreateWhiteChessPieceMaterial(const Transform &xform,
        const TextureParams &mp) {
	float Kd[3] = { .5, .5, .5 };
	float Ks[3] = { .5, .5, .5 };
	float Ksss[3] = { .5, .5, .5 };
	Reference<Texture<Spectrum> > kd = mp.GetSpectrumTexture("Kd", Spectrum::FromRGB(Kd));
	Reference<Texture<Spectrum> > ks = mp.GetSpectrumTexture("Ks", Spectrum::FromRGB(Ks));
	Reference<Texture<Spectrum> > ksss = mp.GetSpectrumTexture("Ksss", Spectrum::FromRGB(Ksss));
	Reference<Texture<float> > uroughness = mp.GetFloatTexture("uroughness", .1f);
	Reference<Texture<float> > vroughness = mp.GetFloatTexture("vroughness", .1f);
	Reference<Texture<float> > mfp = mp.GetFloatTexture("meanfreepath", 1.f);
	Reference<Texture<float> > ior = mp.GetFloatTexture("index", 1.3f);
	Reference<Texture<float> > scale = mp.GetFloatTexture("scale", 1.f);
	Reference<Texture<Spectrum> > kr = mp.GetSpectrumTexture("Kr", Spectrum(1.f));
	Reference<Texture<float> > bumpMap = mp.GetFloatTextureOrNull("bumpmap");
	return new WhiteChessPieceMaterial(kd, ks, uroughness, vroughness, kr, ksss, mfp, ior, scale, bumpMap);
}


