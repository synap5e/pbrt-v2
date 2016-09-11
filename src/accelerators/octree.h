#if defined(_MSC_VER)
#pragma once
#endif

#ifndef PBRT_ACCELERATORS_OCTREEACCEL_H
#define PBRT_ACCELERATORS_OCTREEACCEL_H

// accelerators/octree.h*
#include "pbrt.h"
#include "primitive.h"

class OctreeAccel : public Aggregate {
public:
    // Octree Public Methods
    OctreeAccel(const vector<Reference<Primitive> > &p, int leaf_size);
    BBox WorldBound() const { return bounds; }
    bool CanIntersect() const { return true; }
    ~OctreeAccel();
    bool Intersect(const Ray &ray, Intersection *isect) const;
    bool IntersectP(const Ray &ray) const;
private:
    OctreeAccel(BBox bounds, int leaf_size);
    bool isLeaf() const;
    void insert(Reference<Primitive> p);

    Point center;
    BBox bounds;
    vector<Reference<Primitive> > primitives;
    OctreeAccel *children[8];

    int leaf_size;
    int depth = 0;
};


OctreeAccel *CreateOctreeAccelerator(const vector<Reference<Primitive> > &prims, const ParamSet &ps);

#endif // PBRT_ACCELERATORS_OCTREEACCEL_H
