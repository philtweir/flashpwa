import sys
import json
import re
from random import randint
from pathlib import Path
from random import choice, choices
from colorama import init, Fore, Back, Style
from gramadan.v2.noun import Noun
from gramadan.v2.np import NP
from gramadan.v2.pp import PP
from gramadan.v2.vp import VP
from gramadan.v2.adjective import Adjective
from gramadan.v2.preposition import Preposition
from gramadan.features import Number, Mutation
from gramadan.v2.verb import VPTense, VPShape, VPPolarity, VPPerson
from gramadan.verb import VerbPerson
from gramadan.v2.cnp import CNP
from gramadan.v2.features import Case, Article, System, Gender
from gramadan.v2.database import Database

init()

SAMPLES = 1000

class ComplexPreposition:
  def __init__(self, phrase: str):
    self.phrase = phrase

  def __str__(self):
    return self.phrase

def get_a_form(prep: ComplexPreposition | Preposition | None, noun: Noun, adj: Adjective, with_art: bool, is_plural: bool, expected_gen: bool = False):
  prefix_str: str | None
  number = Number.Pl if is_plural else Number.Sg
  article = Article.Art if with_art else Article.NoArt
  system = System.N
  if isinstance(prep, Preposition):
    expected_gen = False # simple prepositions do not give genitive
    prefix_str = None
    np = noun + adj
    phrase = prep + np
    form = phrase.to(number, article, system if with_art and not is_plural else None)[0].value
  elif isinstance(prep, ComplexPreposition) or expected_gen:
    prefix_str = None
    phrase = noun + adj
    form = phrase.to(Case.Gen, number, article)[0].value
  elif prep is None:
    prefix_str = None
    phrase = noun + adj
    form = phrase.to(Case.Nom, number)[0].value
    if with_art:
      article = "na" if is_plural else "an"
      form = f"{article} {form.value}"
  else:
    raise RuntimeError(f"Preposition is not recognized: {prep}")

  if prefix_str:
    form = f"{prefix_str} {form}"
  return form

def load(data_folder):
  database = Database(data_folder)
  database.load()
  return database.dictionary

class Maker:
  def __init__(self, dictionaries):
    self.dictionaries = dictionaries

  def make(self, line, focail, briathar, siombail_dir, siombail_indir):
    #verb = self.dictionaries["verb"][verb]
    nouns = list(self.dictionaries["noun"])
    verb = self.dictionaries["verb"][briathar[1:-1]]
    siombail_dir = [(sym, self.dictionaries["noun"][choice(nouns)]) for sym in siombail_dir]
    siombail_indir = [(sym, self.dictionaries["noun"][choice(nouns)]) for sym in siombail_indir]
    siombail_dir.reverse()
    siombail_indir.reverse()

    sibhíocht = None
    direct = []
    indirect = []
    original_line = line
    for grúpa in (siombail_dir, siombail_indir):
      altanna = [True] + [choice((True, False)) for _ in list(grúpa[1:])]
      iolraí = [choice((True, False)) for _ in list(grúpa)]
      for ((sym, choi), (_, orig_choi), alt, iolra) in zip(grúpa, grúpa, altanna, iolraí):
        number = Number.Pl if (iolra and choi.plNom) else Number.Sg
        choi = NP.create_from_noun(choi)
        prep = None
        base = None
        is_definite = choi.is_definite
        if grúpa == siombail_indir:
          match = re.match(r"\(([^+]+)\+\)", sym)
          if match:
            prep = match.group(1).strip()
            if prep:
              prep = self.dictionaries["preposition"][prep]
              base = choi
              choi = PP.create(prep, choi)

        gender = choi.getGender()
        if sym == "-":
          sibhíocht = (sym, iolra, gender)

        # print(choi.isDefinite, choi.forms)
        if prep:
          if alt and not is_definite:
            if number == Number.Sg:
              choi = choi.to(number, System.N, Article.Art)[0].value
            else:
              choi = choi.to(number, Article.Art)[0].value
          else:
            choi = choi.to(number)[0].value

        elif choi.isDefinite or not alt:
          choi = choi.to(number, Case.Nom)[0].value
        else:
          choi = choi.to(number, Case.Nom, Article.Art)[0].value
        if base:
          if base.isDefinite or not alt:
            base = base.to(number, Case.Nom)[0].value
          else:
            base = base.to(number, Case.Nom, Article.Art)[0].value

        if grúpa == siombail_indir:
          indirect.append((sym, choi, prep, base, iolra, gender, orig_choi))
        else:
          direct.append((sym, choi, iolra, gender, orig_choi))

    def _make_line(line, vp, ignore, shape):
      subject = None
      subject_id = None
      line_code = str(line)
      line_coded: dict[str, str | list[str]] = {}
      for n_d, (sym, choi, iolra, gender, orig_choi) in enumerate(direct):
        if ignore and ignore[0] == sym:
          line = re.sub(r"([^-+ ]|^)\s*" + re.escape(sym) + r"+\s*([^-+ ]|^)", "\\1 \\2", line)
          line_code = re.sub(r"([^-+ ]|^)\s*" + re.escape(sym) + r"+\s*([^-+ ]|^)", "\\1 \\2", line_code)
          # TODO: check that moving from RelDepDir to RelIndep has not broken by moving from semantics to syntax
          if polarity == VPPolarity.Pos:
            shape = VPShape.RelIndep
          else:
            shape = VPShape.Interrog # Rel dependent is usual dependent
          subject = choi
          subject_id = f"D{n_d}"
        else:
          line = re.sub(r"([^+-]|^)" + re.escape(sym) + r"([^+-]|^)", f"\\1{Fore.GREEN}{choi}{Style.RESET_ALL}\\2", line)
          line_code = re.sub(r"([^+-]|^)" + re.escape(sym) + r"([^+-]|^)", f"\\1${{D{n_d}}}\\2", line_code)
        line_coded[f"D{n_d}"] = [str(orig_choi), str(choi)]
      for n_i, (sym, choi, prep, base, iolra, gender, orig_choi) in enumerate(indirect):
        if ignore and ignore[0] == sym:
          subject = base
          subject_id = f"I{n_i}"
          if iolra:
            choi = prep.forms["pl3"][0].value
          else:
            choi = prep.forms["sg3" + ("Masc" if gender == Gender.Masc else "Fem")][0].value
          shape = VPShape.Interrog
        line = re.sub(r"([^+-]|^)" + re.escape(sym) + r"([^+-]|^)", f"\\1{Fore.YELLOW}{choi}{Style.RESET_ALL}\\2", line)
        line_code = re.sub(r"([^+-]|^)" + re.escape(sym) + r"([^+-]|^)", f"\\1${{I{n_i}}}\\2", line_code)
        line_coded[f"I{n_i}"] = [str(orig_choi), str(choi)]
      ó_bhriathar = vp.tenses[tense][shape][person_form][polarity][0].value
      line = line.replace(briathar, f"{Fore.MAGENTA}{ó_bhriathar}{Style.RESET_ALL}")
      line_code = line_code.replace(briathar, ó_bhriathar)
      line_coded["_root"] = briathar.replace("[", "").replace("]", "")
      if subject:
        line = f"{Fore.RED}{subject}{Style.RESET_ALL} {line}"
        line_code = f"${{{subject_id}}} {line_code}"
      line_coded["_coded"] = line_code
      # TODO: remove gap between a and tá (sim. for abair)
      return (line, line_coded)

    vp = VP.from_verb(verb)
    sym, iolra, gender = sibhíocht
    person_form = VPPerson.NoSubject
    tense = choice([t for t in VPTense if t not in (VPTense.Any, VPTense.Pres, VPTense.PastCont, VPTense.Cond)])
    shape = choices([VPShape.Declar, VPShape.Interrog], weights=(0.3, 0.7))[0]
    polarity = choices([VPPolarity.Neg, VPPolarity.Pos], weights=(0.3, 0.7))[0]
    lines = [
        ("Unchanged", *_make_line(line, vp, None, shape))
    ]
    for d in direct:
      lines.append(("DIRECT", *_make_line(line, vp, d, shape)))
    for ind in indirect:
      lines.append(("INDIRECT", *_make_line(line, vp, ind, shape)))

    #form = get_a_form(prep, noun, adjective, with_art, is_plural, expected_gen=expected_gen)
    return lines

def parse_line(line: str):
  line = line.strip()
  match = re.match(r"\[[^]]+\]", line)
  briathar = match.group(0)
  páirtí = re.split(r"(-+|\([^)]+\))", line)
  if not páirtí:
    raise RuntimeError("Line missing match")
  focail = [x.strip() for x in páirtí[::2]]
  siombail_dir = {p for p in páirtí[1::2] if p.endswith("-")}
  siombail_indir = {p for p in páirtí[1::2] if p.endswith("+)")}
  return [focail, briathar, siombail_dir, siombail_indir]

def run(data_folder):
  dictionaries = load(data_folder)
  COP = dictionaries["copula"]["is"]
  noun = list(dictionaries["noun"].values())[0]
  np = NP.create_from_noun(noun)
  cnp = CNP.create_from_noun_phrases(COP, np, VPPerson.Sg1)
  maker = Maker(dictionaries)
  with Path("examples-cc.txt").open() as exf:
    lines = exf.readlines()
  samples = []
  for _ in range(SAMPLES):
    line = lines[randint(0, len(lines) - 1)]
    focail, briathar, siombail_dir, siombail_indir = parse_line(line)
    results = maker.make(line, focail, briathar, siombail_dir, siombail_indir)
    print(line.strip())
    group = []
    for key, result, line_coded in results:
      print("->", key, result)
      group.append([key, line_coded])
    print()
    samples.append(group)

  with Path("examples.json").open("w") as ouf:
    json.dump(samples, ouf, indent=2)

if __name__ == "__main__":
  run(sys.argv[1])
