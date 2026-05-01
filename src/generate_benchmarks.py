#!/usr/bin/env python3
"""Generate larger synthetic benchmark files for 3806ICT Assignment 1.
The generator deliberately mixes easy, medium and harder formula shapes rather than
repeating only trivial A -> A examples.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'datasets'
DATA.mkdir(exist_ok=True)

def write(path, rows):
    with open(path, 'w', encoding='utf8') as f:
        f.write('# Generated benchmark file. One named formula per line.\n')
        for name, formula in rows:
            f.write(f'{name}: {formula}\n')

# 120 propositional formulae: mixture of tautologies and invalid formulae.
prop=[]
for i in range(1, 21):
    A=f'A{i}'; B=f'B{i}'; C=f'C{i}'
    prop.append((f'prop_identity_{i:02d}', f'{A} -> {A}'))
    prop.append((f'prop_excluded_middle_{i:02d}', f'{A} or not {A}'))
    prop.append((f'prop_and_comm_{i:02d}', f'({A} and {B}) -> ({B} and {A})'))
    prop.append((f'prop_or_comm_{i:02d}', f'({A} or {B}) -> ({B} or {A})'))
    prop.append((f'prop_invalid_strengthen_{i:02d}', f'{A} -> ({A} and {B})'))
    prop.append((f'prop_invalid_or_to_and_{i:02d}', f'({A} or {B}) -> ({A} and {B})'))
write(DATA/'generated_large_propositional.fol', prop)

# 120 medium propositional formulae using nested implication/distribution forms.
medium=[]
for i in range(1, 21):
    A=f'MA{i}'; B=f'MB{i}'; C=f'MC{i}'
    medium.append((f'medium_transitivity_{i:02d}', f'(({A} -> {B}) and ({B} -> {C})) -> ({A} -> {C})'))
    medium.append((f'medium_distrib_valid_{i:02d}', f'({A} and ({B} or {C})) -> (({A} and {B}) or ({A} and {C}))'))
    medium.append((f'medium_demorgan_valid_{i:02d}', f'not ({A} or {B}) -> (not {A} and not {B})'))
    medium.append((f'medium_case_valid_{i:02d}', f'(({A} -> {C}) and ({B} -> {C})) -> (({A} or {B}) -> {C})'))
    medium.append((f'medium_invalid_converse_{i:02d}', f'({A} -> {B}) -> ({B} -> {A})'))
    medium.append((f'medium_invalid_demorgan_reverse_{i:02d}', f'(not {A} or not {B}) -> not ({A} or {B})'))
write(DATA/'generated_large_medium.fol', medium)

# 120 first-order and quantifier-oriented formulae. Some are valid, some are not.
quant=[]
for i in range(1, 21):
    P=f'P{i}'; Q=f'Q{i}'; R=f'R{i}'
    quant.append((f'fo_forall_to_exists_{i:02d}', f'(forall x. {P}(x)) -> (exists x. {P}(x))'))
    quant.append((f'fo_exists_weaken_{i:02d}', f'(exists x. {P}(x)) -> (exists x. ({P}(x) or {Q}(x)))'))
    quant.append((f'fo_exists_forall_to_forall_exists_{i:02d}', f'(exists x. forall y. {R}(x,y)) -> (forall y. exists x. {R}(x,y))'))
    quant.append((f'fo_and_split_{i:02d}', f'(forall x. ({P}(x) and {Q}(x))) -> ((forall x. {P}(x)) and (forall x. {Q}(x)))'))
    quant.append((f'fo_invalid_exists_to_forall_{i:02d}', f'(exists x. {P}(x)) -> (forall x. {P}(x))'))
    quant.append((f'fo_invalid_exists_swap_{i:02d}', f'(exists x. forall y. {R}(x,y)) -> (exists y. forall x. {R}(x,y))'))
write(DATA/'generated_large_quantifier.fol', quant)

print('Generated', len(prop)+len(medium)+len(quant), 'formulae in 3 files')
