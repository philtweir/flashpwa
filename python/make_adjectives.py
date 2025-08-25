import sys
import re
from pathlib import Path
from gramadan.v2.noun import Noun
from gramadan.v2.adjective import Adjective
from gramadan.v2.preposition import Preposition
from gramadan.features import Number
from gramadan.v2.features import Case, Article, System
from gramadan.v2.database import Database

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
      form = f"{article} {form}"
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

  def make(self, noun: str, adjective: str, prefix: str | None = None, with_art: bool = False, is_plural: bool = False, expected_gen: bool = False):
    prep = None
    if prefix in self.dictionaries["preposition"]:
      prep = self.dictionaries["preposition"][prefix]
      prefix = ""
    elif prefix is None:
      prefix = ""
    else:
      prefix = f"{prefix} "

    adjective = self.dictionaries["adjective"][adjective]
    noun = self.dictionaries["noun"][noun]
    form = get_a_form(prep, noun, adjective, with_art, is_plural, expected_gen=expected_gen)
    return f"{prefix}{form}"

def parse_line(line: str):
  match = re.search(r"\((.*)\)", line)
  if not match:
    raise RuntimeError("Line missing match")
  inner = match.group(1).split(" ")
  kwargs: dict[str, bool | str] = {"is_plural": False, "with_art": False}
  if inner[-1] == "*":
    kwargs["is_plural"] = True
    inner.pop()
  adjective = inner.pop()
  noun = inner.pop()
  if inner and inner[-1] in ("an", "na"):
    kwargs["with_art"] = True
    inner.pop()

  # This ignores prefixes that do not trigger genitive,
  # such as [ag X N A] for verbal noun X
  prefix = " ".join(inner)
  if prefix:
    kwargs["expected_gen"] = True
    kwargs["prefix"] = prefix
  return [noun, adjective], kwargs

def run(data_folder):
  dictionaries = load(data_folder)
  maker = Maker(dictionaries)
  with Path("examples.txt").open() as exf:
    lines = exf.readlines()
  for line in lines:
    args, kwargs = parse_line(line)
    result = maker.make(*args, **kwargs)
    print(line.strip())
    print("->", result)
    print()


if __name__ == "__main__":
  run(sys.argv[1])
