"""Combinatorial FieldSpace coverage only; no physical-sector solver."""
from itertools import combinations
from collections import Counter
import math

SECTORS = ("E","M","S","F","W","T","I","R","H","P","A")

def atlas():
    return [dict(id=f"FS-{i:03d}",sectors=list(t),dynamics_implemented=False)
            for i,t in enumerate(combinations(SECTORS,3),1)]

def coverage(sectors, order):
    if len(set(sectors)) != len(sectors) or not set(sectors) <= set(SECTORS):
        raise ValueError("Unknown or duplicate FieldSpace sectors")
    if type(order) is not int or order < 1 or order > len(sectors):
        raise ValueError("order must be in 1..number of selected sectors")
    requirements = list(combinations(sectors,order))
    triples = [set(t["sectors"]) for t in atlas()]
    missing = [list(t) for t in requirements if not any(set(t) <= x for x in triples)]
    return dict(order=order,requirements=len(requirements),covered=len(requirements)-len(missing),
                missing=missing,scope="combinatorial_only",physical_validation=False)

def verify_atlas():
    triples = [set(x["sectors"]) for x in atlas()]
    incidences = {s:sum(s in t for t in triples) for s in SECTORS}
    pairs = {"-".join(p):sum(set(p)<=t for t in triples) for p in combinations(SECTORS,2)}
    overlap = Counter(len(a&b) for a,b in combinations(triples,2))
    return dict(sectors=11,triplets=len(triples),sector_incidence=incidences,pair_incidence=pairs,
                overlap_spectrum=dict(overlap),passed=len(triples)==math.comb(11,3)
                and set(incidences.values())=={45} and set(pairs.values())=={9}
                and overlap=={0:4620,1:6930,2:1980},method="Python exhaustive enumeration, not a new Lean proof")
