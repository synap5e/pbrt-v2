// accelerators/octree.cpp*
#include "stdafx.h"
#include "accelerators/octree.h"
#include "paramset.h"

OctreeAccel::OctreeAccel(BBox bounds, int leaf_size): bounds(bounds), leaf_size(leaf_size){
    center = (bounds.pMax + bounds.pMin) / 2.f;
    for(int i=0; i<8; ++i){
        children[i] = nullptr;
    }
}

OctreeAccel::OctreeAccel(const vector<Reference<Primitive>> &prims, int leaf_size): leaf_size(leaf_size){
    for(int i=0; i<8; ++i){
        children[i] = nullptr;
    }

    // compute bounds
    if (prims.size() > 0){
        bounds = prims[0]->WorldBound();
    }
    for (auto e : prims){
        bounds = Union(bounds, e->WorldBound());
    }
    center = (bounds.pMax + bounds.pMin) / 2.f;

    for (auto e : prims){
        if (!e->CanIntersect()){
            vector<Reference<Primitive> > p;
            e->FullyRefine(p);
            for (auto sube : p){
                insert(sube);
            }
        } else {
            insert(e);
        }
    }
}

OctreeAccel::~OctreeAccel() {
    for(int i=0; i<8; ++i){
        delete children[i];
    }
}

bool OctreeAccel::isLeaf() const{
    return children[0] == nullptr;
}

void OctreeAccel::insert(Reference<Primitive> p){
    if (!bounds.Overlaps(p->WorldBound())){
        return;
    }

    if (isLeaf()){
        primitives.push_back(p);
        if (int(primitives.size()) > leaf_size){
            Vector dimension = bounds.pMax - bounds.pMin;
            dimension /= 2.f;
            for(int i=0; i<8; ++i) {
                Point newCenter = center;
                newCenter.x += dimension.x * (i&4 ? .5f : -.5f);
                newCenter.y += dimension.y * (i&2 ? .5f : -.5f);
                newCenter.z += dimension.z * (i&1 ? .5f : -.5f);
                BBox newBounds = BBox(newCenter - dimension / 2, newCenter + dimension / 2);
                children[i] = new OctreeAccel(newBounds, leaf_size);
                children[i]->depth = depth + 1;
            }

            for (auto e : primitives){
                insert(e);
            }
            primitives.clear();
        }
    } else {
        for(int i=0; i<8; ++i) {
            children[i]->insert(p);
        }
    }
}

bool OctreeAccel::Intersect(const Ray &ray, Intersection *isect) const {
    bool hit = false;
    float tmin, tmax;
    if (!bounds.IntersectP(ray, &tmin, &tmax)){
        return false;
    }

    if (isLeaf()){
        for (auto e : primitives){
            hit |= e->Intersect(ray, isect);
        }
    } else {
        for(int i=0; i<8; ++i) {
            hit |= children[i]->Intersect(ray, isect);
        }
    }

    return hit;
}


bool OctreeAccel::IntersectP(const Ray &ray) const {
    float tmin, tmax;
    if (!bounds.IntersectP(ray, &tmin, &tmax)){
        return false;
    }

    if (isLeaf()){
        for (auto e : primitives){
            if (e->IntersectP(ray)){
                return true;
            }
        }
    } else {
        for(int i=0; i<8; ++i) {
            if( children[i]->IntersectP(ray)){
                return true;
            }
        }
    }
    return false;
}


OctreeAccel *CreateOctreeAccelerator(const vector<Reference<Primitive> > &prims, const ParamSet &ps) {
    return new OctreeAccel(prims, ps.FindOneInt("leaf_size", 25));
}


