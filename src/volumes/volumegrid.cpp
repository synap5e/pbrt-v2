
/*
    pbrt source code Copyright(c) 1998-2010 Matt Pharr and Greg Humphreys.

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


// volumes/volumegrid.cpp*
#include "stdafx.h"
#include "volumes/volumegrid.h"
#include "paramset.h"

// VolumeGridDensity Method Definitions
float VolumeGridDensity::Density(const Point &Pobj) const {
    if (!extent.Inside(Pobj)) return 0;
    // Compute voxel coordinates and offsets for _Pobj_
    Vector vox = extent.Offset(Pobj);
    vox.x = vox.x * nx - .5f;
    vox.y = vox.y * ny - .5f;
    vox.z = vox.z * nz - .5f;
    int vx = Floor2Int(vox.x), vy = Floor2Int(vox.y), vz = Floor2Int(vox.z);
    float dx = vox.x - vx, dy = vox.y - vy, dz = vox.z - vz;

    // Trilinearly interpolate density values to compute local density
    float d00 = Lerp(dx, D(vx, vy, vz),     D(vx+1, vy, vz));
    float d10 = Lerp(dx, D(vx, vy+1, vz),   D(vx+1, vy+1, vz));
    float d01 = Lerp(dx, D(vx, vy, vz+1),   D(vx+1, vy, vz+1));
    float d11 = Lerp(dx, D(vx, vy+1, vz+1), D(vx+1, vy+1, vz+1));
    float d0 = Lerp(dy, d00, d10);
    float d1 = Lerp(dy, d01, d11);
	float amount = Lerp(dz, d0, d1);
	return amount <= 0.2? 0 : amount;
}

// VolumeGridDensity Method Definitions
Spectrum VolumeGridDensity::Color(const Point &Pobj) const {
	if (!extent.Inside(Pobj)) return 0;
	// Compute voxel coordinates and offsets for _Pobj_
	Vector vox = extent.Offset(Pobj);
	vox.x = vox.x * nx - .5f;
	vox.y = vox.y * ny - .5f;
	vox.z = vox.z * nz - .5f;
	int vx = Floor2Int(vox.x), vy = Floor2Int(vox.y), vz = Floor2Int(vox.z);
	float dx = vox.x - vx, dy = vox.y - vy, dz = vox.z - vz;

	// Trilinearly interpolate density values to compute local density
	float r00 = Lerp(dx, C(vx, vy, vz, 0), C(vx + 1, vy, vz, 0));
	float r10 = Lerp(dx, C(vx, vy + 1, vz, 0), C(vx + 1, vy + 1, vz, 0));
	float r01 = Lerp(dx, C(vx, vy, vz + 1, 0), C(vx + 1, vy, vz + 1, 0));
	float r11 = Lerp(dx, C(vx, vy + 1, vz + 1, 0), C(vx + 1, vy + 1, vz + 1, 0));

	float g00 = Lerp(dx, C(vx, vy, vz, 1), C(vx + 1, vy, vz, 1));
	float g10 = Lerp(dx, C(vx, vy + 1, vz, 1), C(vx + 1, vy + 1, vz, 1));
	float g01 = Lerp(dx, C(vx, vy, vz + 1, 1), C(vx + 1, vy, vz + 1, 1));
	float g11 = Lerp(dx, C(vx, vy + 1, vz + 1, 1), C(vx + 1, vy + 1, vz + 1, 1));

	float b00 = Lerp(dx, C(vx, vy, vz, 2), C(vx + 1, vy, vz, 2));
	float b10 = Lerp(dx, C(vx, vy + 1, vz, 2), C(vx + 1, vy + 1, vz, 2));
	float b01 = Lerp(dx, C(vx, vy, vz + 1, 2), C(vx + 1, vy, vz + 1, 2));
	float b11 = Lerp(dx, C(vx, vy + 1, vz + 1, 2), C(vx + 1, vy + 1, vz + 1, 2));

	float r0 = Lerp(dy, r00, r10);
	float r1 = Lerp(dy, r01, r11);
	float rFinal = Lerp(dz, r0, r1);

	float g0 = Lerp(dy, g00, g10);
	float g1 = Lerp(dy, g01, g11);
	float gFinal = Lerp(dz, g0, g1);

	float b0 = Lerp(dy, b00, b10);
	float b1 = Lerp(dy, b01, b11);
	float bFinal = Lerp(dz, b0, b1);
	float col[3] = { Lerp(dz, r0, r1), Lerp(dz, g0, g1), Lerp(dz, b0, b1) };

	Spectrum outColor = Spectrum::FromRGB(col);
	return outColor;
}


VolumeGridDensity *CreateGridVolumeRegion(const Transform &volume2world,
        const ParamSet &params) {
    // Initialize common volume region parameters
    Spectrum sigma_a = params.FindOneSpectrum("sigma_a", 0.);
    Spectrum sigma_s = params.FindOneSpectrum("sigma_s", 0.);
    float g = params.FindOneFloat("g", 0.);
    Spectrum Le = params.FindOneSpectrum("Le", 0.);
    Point p0 = params.FindOnePoint("p0", Point(0,0,0));
    Point p1 = params.FindOnePoint("p1", Point(1,1,1));
    int nitems;
    const float *data = params.FindFloat("density", &nitems);
    if (!data) {
        Error("No \"density\" values provided for volume grid?");
        return NULL;
    }
	int cnitems;
	const float *color = params.FindFloat("color", &cnitems);
	if (!data) {
		Error("No \"color\" values provided for volume grid?");
		return NULL;
	}
    int nx = params.FindOneInt("nx", 1);
    int ny = params.FindOneInt("ny", 1);
    int nz = params.FindOneInt("nz", 1);
    if (nitems != nx*ny*nz) {
        Error("VolumeGridDensity has %d density values but nx*ny*nz = %d",
            nitems, nx*ny*nz);
        return NULL;
    }
	if (cnitems != nx*ny*nz*3) {
		Error("VolumeGridDensity has %d color values but nx*ny*nz*3 = %d",
			cnitems, nx*ny*nz*3);
		return NULL;
	}
    return new VolumeGridDensity(sigma_a, sigma_s, g, Le, BBox(p0, p1),
		volume2world, nx, ny, nz, data, color);
}


