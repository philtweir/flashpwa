#!/usr/bin/env python3
"""
Generate Irish relative clause examples for language learning flashcards.

This script creates grammatical variations of Irish sentences containing relative clauses,
generating both direct and indirect relative clause forms from template sentences.
"""

import sys
import json
import re
from random import randint, choice, choices
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from colorama import init, Fore, Back, Style

# Gramadán imports for Irish language processing
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

# Initialize colorama for colored terminal output
init()

# Configuration
SAMPLES = 1000  # Number of examples to generate
EXAMPLES_INPUT_FILE = "examples-cc.txt"
EXAMPLES_OUTPUT_FILE = "examples.json"


class ComplexPreposition:
    """Represents a complex preposition phrase in Irish."""

    def __init__(self, phrase: str):
        self.phrase = phrase

    def __str__(self):
        return self.phrase


class RelativeClauseGenerator:
    """Generates Irish relative clause variations from template sentences."""

    def __init__(self, dictionaries: Dict[str, Any]):
        """
        Initialize the generator with grammatical dictionaries.

        Args:
            dictionaries: Dictionary containing verb, noun, and preposition data
        """
        self.dictionaries = dictionaries
        self.nouns = list(dictionaries["noun"])

    def parse_template_line(self, line: str) -> Tuple[List[str], str, set, set]:
        """
        Parse a template line to extract verb and placeholder symbols.

        Template format: "[verb] text -D- text (prep+I) text"
        Where:
            - [verb] is the main verb in brackets
            - -D- represents direct object placeholders (ending with -)
            - (prep+I) represents indirect object placeholders (ending with +))

        Args:
            line: Template sentence line

        Returns:
            Tuple of (words, verb, direct_symbols, indirect_symbols)
        """
        line = line.strip()

        # Extract the verb (text in square brackets)
        verb_match = re.match(r"\[[^]]+\]", line)
        if not verb_match:
            raise ValueError(f"No verb found in line: {line}")
        verb = verb_match.group(0)

        # Split line by symbols (direct and indirect placeholders)
        parts = re.split(r"(-+|\([^)]+\))", line)
        if not parts:
            raise ValueError(f"Invalid line format: {line}")

        # Extract components
        words = [x.strip() for x in parts[::2]]  # Text parts
        direct_symbols = {p for p in parts[1::2] if p.endswith("-")}
        indirect_symbols = {p for p in parts[1::2] if p.endswith("+)")}

        return words, verb, direct_symbols, indirect_symbols

    def _select_random_nouns(self, symbols: List[str]) -> List[Tuple[str, Noun]]:
        """
        Assign random nouns to placeholder symbols.

        Args:
            symbols: List of placeholder symbols

        Returns:
            List of (symbol, noun) tuples
        """
        return [(sym, self.dictionaries["noun"][choice(self.nouns)]) 
                for sym in symbols]

    def _process_direct_objects(self, direct_symbols: List[Tuple[str, Noun]], 
                               line: str, line_code: str, 
                               ignore: Optional[Tuple] = None,
                               shape: VPShape = None,
                               polarity: VPPolarity = None) -> Tuple[str, str, Dict, Optional[str], Optional[str], VPShape]:
        """
        Process direct object placeholders in the sentence.

        Args:
            direct_symbols: List of (symbol, noun) pairs for direct objects
            line: The sentence with placeholders
            line_code: The coded version of the sentence
            ignore: Optional symbol to ignore (for relative clause focus)
            shape: Current verb shape
            polarity: Current verb polarity

        Returns:
            Tuple of (processed_line, processed_code, coded_dict, subject, subject_id, updated_shape)
        """
        subject = None
        subject_id = None
        line_coded = {}

        for idx, (symbol, noun_choice, plural, gender, original_noun) in enumerate(direct_symbols):
            tag = f"D{idx}"

            if ignore and ignore[0] == symbol:
                # This is the relativized element - remove it from the sentence
                line = re.sub(r"([^-+ ]|^)\s*" + re.escape(symbol) + r"+\s*([^-+ ]|^)", "\\1 \\2", line)
                line_code = re.sub(r"([^-+ ]|^)\s*" + re.escape(symbol) + r"+\s*([^-+ ]|^)", "\\1 \\2", line_code)

                # Adjust verb shape for relative clause
                if polarity == VPPolarity.Pos:
                    shape = VPShape.RelIndep
                else:
                    shape = VPShape.Interrog

                subject = noun_choice
                subject_id = tag
            else:
                # Replace placeholder with colored noun
                colored = f"{Fore.GREEN}{noun_choice}{Style.RESET_ALL}"
                line = re.sub(r"([^+-]|^)" + re.escape(symbol) + r"([^+-]|^)", 
                            f"\\1{colored}\\2", line)
                line_code = re.sub(r"([^+-]|^)" + re.escape(symbol) + r"([^+-]|^)", 
                                 f"\\1${{{tag}}}\\2", line_code)

            line_coded[tag] = [str(original_noun), str(noun_choice)]

        return line, line_code, line_coded, subject, subject_id, shape

    def _process_indirect_objects(self, indirect_symbols: List[Tuple], 
                                 line: str, line_code: str,
                                 line_coded: Dict,
                                 ignore: Optional[Tuple] = None) -> Tuple[str, str, Dict, Optional[str], Optional[str], VPShape]:
        """
        Process indirect object placeholders in the sentence.

        Args:
            indirect_symbols: List of tuples with indirect object data
            line: The sentence with placeholders
            line_code: The coded version of the sentence
            line_coded: Dictionary of coded elements
            ignore: Optional symbol to ignore (for relative clause focus)

        Returns:
            Tuple of (processed_line, processed_code, updated_coded_dict, subject, subject_id, shape)
        """
        subject = None
        subject_id = None
        shape = VPShape.Interrog

        for idx, (symbol, noun_choice, prep, base, plural, gender, original_noun) in enumerate(indirect_symbols):
            tag = f"I{idx}"

            if ignore and ignore[0] == symbol:
                # This is the relativized element
                subject = base
                subject_id = tag

                # Use prepositional pronoun form
                if plural:
                    noun_choice = prep.forms["pl3"][0].value
                else:
                    gender_suffix = "Masc" if gender == Gender.Masc else "Fem"
                    noun_choice = prep.forms[f"sg3{gender_suffix}"][0].value
                print(plural, noun_choice, base)

            # Replace placeholder with colored noun
            colored = f"{Fore.YELLOW}{noun_choice}{Style.RESET_ALL}"
            line = re.sub(r"([^+-]|^)" + re.escape(symbol) + r"([^+-]|^)", 
                        f"\\1{colored}\\2", line)
            line_code = re.sub(r"([^+-]|^)" + re.escape(symbol) + r"([^+-]|^)", 
                           f"\\1${{{tag}R}}\\2", line_code)

            line_coded[tag] = [str(original_noun), str(base), str(noun_choice)]

        return line, line_code, line_coded, subject, subject_id, shape

    def _prepare_noun_phrases(self, symbols: List[str], is_indirect: bool = False) -> List[Tuple]:
        """
        Prepare noun phrases with grammatical variations.

        Args:
            symbols: List of placeholder symbols
            is_indirect: Whether these are indirect objects (with prepositions)

        Returns:
            List of tuples containing processed noun phrase data
        """
        nouns = self._select_random_nouns(list(symbols))
        nouns.reverse()  # Process in reverse order for some reason (legacy behavior)

        result = []

        # Generate variations: first always definite, others random
        definite_choices = [True] + [choice([True, False]) for _ in nouns[1:]]
        plural_choices = [choice([True, False]) for _ in nouns]

        for (symbol, noun), definite, plural in zip(nouns, definite_choices, plural_choices):
            # Create noun phrase
            if not noun.plNom:
                plural = False
            number = Number.Pl if plural else Number.Sg
            noun_phrase = NP.create_from_noun(noun)

            prep = None
            base = None

            if is_indirect:
                # Extract preposition from symbol like "(ar+)"
                match = re.match(r"\(([^+]+)\+\)", symbol)
                if match:
                    prep_text = match.group(1).strip()
                    if prep_text:
                        prep = self.dictionaries["preposition"][prep_text]
                        base = noun_phrase
                        noun_phrase = PP.create(prep, noun_phrase)

            # Generate the appropriate form
            gender = noun_phrase.getGender()

            if prep and base:
                # Prepositional phrase
                if definite and not base.is_definite:
                    if number == Number.Sg:
                        form = noun_phrase.to(number, System.N, Article.Art)[0].value
                    else:
                        form = noun_phrase.to(number, Article.Art)[0].value
                else:
                    form = noun_phrase.to(number)[0].value

                if base:
                    if base.isDefinite or not definite:
                        base = base.to(number, Case.Nom)[0].value
                    else:
                        base = base.to(number, Case.Nom, Article.Art)[0].value

                result.append((symbol, form, prep, base, plural, gender, noun))
            else:
                # Direct object phrase
                if noun_phrase.isDefinite or not definite:
                    form = noun_phrase.to(number, Case.Nom)[0].value
                else:
                    form = noun_phrase.to(number, Case.Nom, Article.Art)[0].value

                result.append((symbol, form, plural, gender, noun))

        return result

    def generate_variations(self, line: str, words: List[str], verb_text: str, 
                           direct_symbols: set, indirect_symbols: set) -> List[Tuple[str, Dict]]:
        """
        Generate relative clause variations of a sentence.

        Creates three versions:
        1. Unchanged - the base sentence with all placeholders filled
        2. Direct - relative clauses focusing on each direct object
        3. Indirect - relative clauses focusing on each indirect object

        Args:
            line: Template sentence
            words: Parsed words from the sentence
            verb_text: The verb in brackets
            direct_symbols: Set of direct object symbols
            indirect_symbols: Set of indirect object symbols

        Returns:
            List of (type, coded_sentence) tuples
        """
        # Get verb and prepare noun phrases
        verb = self.dictionaries["verb"][verb_text[1:-1]]  # Remove brackets
        verb_phrase = VP.from_verb(verb)

        # Prepare direct and indirect objects
        direct_objects = self._prepare_noun_phrases(direct_symbols, is_indirect=False)
        indirect_objects = self._prepare_noun_phrases(indirect_symbols, is_indirect=True)

        # Select random verb forms
        tense = choice([t for t in VPTense 
                       if t not in (VPTense.Any, VPTense.Pres, VPTense.PastCont, VPTense.Cond)])
        shape = choices([VPShape.Declar, VPShape.Interrog], weights=[0.3, 0.7])[0]
        polarity = choices([VPPolarity.Neg, VPPolarity.Pos], weights=[0.3, 0.7])[0]
        person_form = VPPerson.NoSubject

        variations = []

        # Helper function to create a variation
        def create_variation(ignore_element: Optional[Tuple] = None) -> Tuple[str, Dict]:
            """Create a single variation of the sentence."""
            current_line = str(line)
            current_code = str(line)
            current_shape = shape

            # Process direct objects
            current_line, current_code, coded, subject, subject_id, current_shape = \
                self._process_direct_objects(direct_objects, current_line, current_code, 
                                           ignore_element, current_shape, polarity)

            # Process indirect objects
            current_line, current_code, coded, ind_subject, ind_subject_id, ind_shape = \
                self._process_indirect_objects(indirect_objects, current_line, current_code, 
                                             coded, ignore_element)

            # Update subject if from indirect object
            if ind_subject:
                subject = ind_subject
                subject_id = ind_subject_id
                current_shape = ind_shape

            # Apply verb conjugation
            verb_form = verb_phrase.tenses[tense][current_shape][person_form][polarity][0].value
            colored_verb = f"{Fore.MAGENTA}{verb_form}{Style.RESET_ALL}"
            current_line = current_line.replace(verb_text, colored_verb)
            current_code = current_code.replace(verb_text, verb_form)
            coded["_root"] = verb_text.replace("[", "").replace("]", "")

            # Add subject if this is a relative clause
            if subject:
                current_line = f"{Fore.RED}{subject}{Style.RESET_ALL} {current_line}"
                current_code = f"${{{subject_id}}} {current_code}"

            coded["_coded"] = current_code

            return current_line, coded

        # Generate unchanged version
        unchanged_line, unchanged_coded = create_variation(None)
        variations.append(("Unchanged", unchanged_coded))

        # Generate direct relative clause variations
        for direct_obj in direct_objects:
            direct_line, direct_coded = create_variation(direct_obj)
            variations.append(("DIRECT", direct_coded))

        # Generate indirect relative clause variations
        for indirect_obj in indirect_objects:
            indirect_line, indirect_coded = create_variation(indirect_obj)
            variations.append(("INDIRECT", indirect_coded))

        # Print colored output for debugging
        print(line.strip())
        for variation_type, coded in variations:
            if "_coded" in coded:
                print(f"-> {variation_type}: {coded.get('_coded', '')}")
        print()

        return variations


def load_gramadan_database(data_folder: str) -> Dict[str, Any]:
    """
    Load the Gramadán database containing Irish language data.

    Args:
        data_folder: Path to the Gramadán data folder

    Returns:
        Dictionary of grammatical elements
    """
    database = Database(data_folder)
    database.load()
    return database.dictionary


def main(data_folder: str):
    """
    Main function to generate relative clause examples.

    Args:
        data_folder: Path to the Gramadán data folder
    """
    # Load grammatical data
    print("Loading Gramadán database...")
    dictionaries = load_gramadan_database(data_folder)

    # Initialize generator
    generator = RelativeClauseGenerator(dictionaries)

    # Load template sentences
    template_file = Path(EXAMPLES_INPUT_FILE)
    if not template_file.exists():
        raise FileNotFoundError(f"Template file not found: {EXAMPLES_INPUT_FILE}")

    print(f"Reading templates from {EXAMPLES_INPUT_FILE}...")
    with template_file.open() as f:
        template_lines = f.readlines()

    # Generate examples
    print(f"Generating {SAMPLES} examples...")
    examples = []

    for i in range(SAMPLES):
        # Select random template
        template = template_lines[randint(0, len(template_lines) - 1)]

        try:
            # Parse template
            words, verb, direct_symbols, indirect_symbols = \
                generator.parse_template_line(template)

            # Generate variations
            variations = generator.generate_variations(
                template, words, verb, direct_symbols, indirect_symbols
            )

            # Store results (without the display strings, just the coded versions)
            example_group = []
            for variation_type, coded_data in variations:
                example_group.append([variation_type, coded_data])

            examples.append(example_group)

        except Exception as e:
            print(f"Error processing line {i}: {template.strip()}")
            print(f"  Error: {e}")
            continue

    # Save to JSON
    output_file = Path(EXAMPLES_OUTPUT_FILE)
    print(f"Saving {len(examples)} examples to {EXAMPLES_OUTPUT_FILE}...")
    with output_file.open("w") as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated {len(examples)} examples!")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_clásal_coibhneasta.py <gramadan_data_folder>")
        sys.exit(1)

    main(sys.argv[1])
