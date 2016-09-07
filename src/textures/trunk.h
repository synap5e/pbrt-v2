#if defined(_MSC_VER)
#pragma once
#endif

#ifndef PBRT_TEXTURES_TRUNK_H
#define PBRT_TEXTURES_TRUNK_H

// textures/trunk.h*
#include "pbrt.h"
#include "texture.h"
#include "paramset.h"

// TrunkTexture Declarations
class TrunkTexture : public Texture<Spectrum> {
public:
    // TrunkTexture Public Methods
    ~TrunkTexture() {
        delete mapping;
    }
    TrunkTexture(float ring_smoothness, float ring_count, float ring_variation, float variation_resolution, Spectrum trunk, Spectrum ring, TextureMapping3D *map):
        ring_smoothness(ring_smoothness),
        ring_count(ring_count),
        ring_variation(ring_variation),
        variation_resolution(variation_resolution),
        trunk(trunk),
        ring(ring),
        mapping(map) {}
    Spectrum Evaluate(const DifferentialGeometry &dg) const;
private:
    // TrunkTexture Private Data
    float ring_smoothness, ring_count, ring_variation, variation_resolution;
    Spectrum trunk, ring;
    TextureMapping3D *mapping;
};


Texture<float> *CreateTrunkFloatTexture(const Transform &tex2world,
        const TextureParams &tp);
TrunkTexture *CreateTrunkSpectrumTexture(const Transform &tex2world,
        const TextureParams &tp);

#endif // PBRT_TEXTURES_TRUNK_H
