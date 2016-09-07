// textures/trunk.cpp*
#include "stdafx.h"
#include "textures/trunk.h"

// TrunkTexture Method Definitions
Texture<float> *CreateTrunkFloatTexture(const Transform &tex2world, const TextureParams &tp) {
    return NULL;
}

TrunkTexture *CreateTrunkSpectrumTexture(const Transform &tex2world, const TextureParams &tp) {
    // compute a new basis using the "trunk_up" vector and the specified "trunk_center"
    Vector trunkUp = Normalize(tp.FindVector("trunk_up", Vector(0, 1, 0)));
    Vector right = Vector(1, 0, 0);
    if (trunkUp == right){
        right = Vector(0, 0, 1);
    }
    Vector forwards = Cross(right, trunkUp);
    right = Cross(trunkUp, forwards);
    Point trunk_center = tp.FindPoint("trunk_center", Point(0, 0, 0));
    Matrix4x4 basis = Matrix4x4::Mul(
        Matrix4x4(
            right.x, trunkUp.x, forwards.x, 0.f,
            right.y, trunkUp.y, forwards.y, 0.f,
            right.z, trunkUp.z, forwards.z, 0.f,
            0.f,     0.f,       0.f,        1.f
        ),
        Matrix4x4(
            1.f, 0.f, 0.f, -trunk_center.x,
            0.f, 1.f, 0.f, -trunk_center.y,
            0.f, 0.f, 1.f, -trunk_center.z,
            0.f, 0.f, 0.f, 1.f
        )
    );

    static float trunkRGB[3] = {1, 0.5, 0.05};
    static float ringRGB[3] = {0.1, 0.01, 0};
    return new TrunkTexture(
        tp.FindFloat("ring_smoothness", 8),
        tp.FindFloat("ring_count", 24),
        tp.FindFloat("ring_variation", 4),
        tp.FindFloat("variation_resolution", 8),
        tp.FindSpectrum("trunk", Spectrum::FromRGB(trunkRGB)),
        tp.FindSpectrum("ring", Spectrum::FromRGB(ringRGB)),
        new IdentityMapping3D(tex2world * basis)
    );
}

Spectrum TrunkTexture::Evaluate(const DifferentialGeometry &dg) const{
    Vector dpdx, dpdy;
    Point P = mapping->Map(dg, &dpdx, &dpdy);

    float x = P.x * ((ring_smoothness+3.f)/10.f);
    float y = P.z * ((ring_smoothness+3.f)/10.f);

    float rings = sqrt(x * x + y * y);
    float noise = (ring_variation/100.f) * Turbulence(P, dpdx, dpdy, 1.f, variation_resolution);

    float scale = ring_count / ((ring_smoothness+3.f)/10.f);
    float pos = (rings + noise) * scale;

    float val = 0.5f * fabs(sin(pos));

    return Lerp(val, ring, trunk);
}