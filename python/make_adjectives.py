#!/usr/bin/env python3
"""
Generate Irish adjective mutation examples for language learning flashcards.

This script creates grammatical variations of Irish adjective phrases showing
mutation patterns for articles, nouns, and adjectives in different contexts.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from random import choice, randint

# Gramadán imports for Irish language processing
from gramadan.v2.noun import Noun
from gramadan.v2.adjective import Adjective
from gramadan.v2.preposition import Preposition
from gramadan.features import Number
from gramadan.v2.features import Case, Article, System
from gramadan.v2.database import Database

# Configuration
SAMPLES = 100  # Number of examples to generate
EXAMPLES_INPUT_FILE = "examples.txt"
ADJECTIVES_OUTPUT_FILE = "adjectives.json"


class AdjectiveExample:
    """Represents a single adjective mutation example."""
    
    def __init__(self, name: str, prefix: str, article: str, article_mut: str,
                 noun: str, noun_mut_front: str, noun_mut_mid: str, noun_mut_back: str,
                 adjective: str, adj_mut_front: str, adj_mut_mid: str, adj_mut_back: str):
        self.name = name
        self.prefix = prefix
        self.article = article
        self.article_mut = article_mut
        self.noun = noun
        self.noun_mut_front = noun_mut_front
        self.noun_mut_mid = noun_mut_mid
        self.noun_mut_back = noun_mut_back
        self.adjective = adjective
        self.adj_mut_front = adj_mut_front
        self.adj_mut_mid = adj_mut_mid
        self.adj_mut_back = adj_mut_back
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format expected by Vue component."""
        return {
            "name": self.name,
            "prefix": self.prefix,
            "article": self.article,
            "articleMut": self.article_mut,
            "noun": self.noun,
            "nounMutFront": self.noun_mut_front,
            "nounMutMid": self.noun_mut_mid,
            "nounMutBack": self.noun_mut_back,
            "adjective": self.adjective,
            "adjMutFront": self.adj_mut_front,
            "adjMutMid": self.adj_mut_mid,
            "adjMutBack": self.adj_mut_back,
        }


class AdjectiveGenerator:
    """Generates Irish adjective mutation examples."""
    
    def __init__(self, dictionaries: Dict[str, Any]):
        """
        Initialize the generator with grammatical dictionaries.
        
        Args:
            dictionaries: Dictionary containing noun, adjective, and preposition data
        """
        self.dictionaries = dictionaries
        self.nouns = list(dictionaries["noun"].keys())
        self.adjectives = list(dictionaries["adjective"].keys())
        self.prepositions = list(dictionaries["preposition"].keys())
    
    def analyze_mutation(self, original: str, mutated: str) -> Tuple[str, str, str]:
        """
        Analyze mutation pattern to split into front/mid/back components.
        
        Args:
            original: Original word form
            mutated: Mutated word form
            
        Returns:
            Tuple of (front_mutation, middle_unchanged, back_mutation)
        """
        if not original or not mutated:
            return "", "", ""
        
        # Find the longest common substring (usually the middle part)
        original_lower = original.lower()
        mutated_lower = mutated.lower()
        
        # Simple approach: find common middle part
        min_len = min(len(original_lower), len(mutated_lower))
        
        # Find common start
        start_common = 0
        for i in range(min_len):
            if original_lower[i] == mutated_lower[i]:
                start_common = i + 1
            else:
                break
        
        # Find common end (working backwards)
        end_common = 0
        for i in range(1, min_len + 1):
            if original_lower[-i] == mutated_lower[-i]:
                end_common = i
            else:
                break
        
        # Extract parts
        if start_common + end_common >= min_len:
            # Mostly common - simple case
            front_mut = mutated[:max(1, start_common)]
            mid_part = mutated[max(1, start_common):len(mutated)-max(0, end_common-1)] if end_common > 1 else mutated[max(1, start_common):]
            back_mut = mutated[len(mutated)-max(0, end_common-1):] if end_common > 1 else ""
        else:
            # More complex - try to find a reasonable split
            # Take first char as front mutation, rest as middle
            front_mut = mutated[:1] if mutated else ""
            mid_part = mutated[1:] if len(mutated) > 1 else ""
            back_mut = ""
        
        return front_mut, mid_part, back_mut
    
    def generate_example(self, noun_key: str, adjective_key: str, 
                        prefix: Optional[str] = None, 
                        with_article: bool = True,
                        is_plural: bool = False) -> AdjectiveExample:
        """
        Generate a single adjective mutation example.
        
        Args:
            noun_key: Key for noun in dictionary
            adjective_key: Key for adjective in dictionary
            prefix: Optional preposition or prefix
            with_article: Whether to include definite article
            is_plural: Whether to use plural form
            
        Returns:
            AdjectiveExample object
        """
        noun = self.dictionaries["noun"][noun_key]
        adjective = self.dictionaries["adjective"][adjective_key]
        
        # Determine forms
        number = Number.Pl if is_plural else Number.Sg
        article_type = Article.Art if with_article else Article.NoArt
        
        # Base forms (nominative)
        noun_phrase = noun + adjective
        base_form = noun_phrase.to(Case.Nom, number, article_type)[0].value
        
        # Get constituent parts
        article_base = ""
        article_mut = ""
        if with_article:
            if is_plural:
                article_base = article_mut = "na"
            else:
                article_base = article_mut = "an"
        
        # Handle preposition
        prep_prefix = ""
        if prefix and prefix in self.dictionaries["preposition"]:
            prep = self.dictionaries["preposition"][prefix]
            prep_phrase = prep + noun_phrase
            mutated_form = prep_phrase.to(number, article_type)[0].value
            prep_prefix = prefix
        else:
            if prefix:
                prep_prefix = prefix
            # Use genitive for mutation example
            mutated_form = noun_phrase.to(Case.Gen, number, article_type)[0].value
        
        # Extract base noun and adjective forms
        base_noun_form = noun.to(Case.Nom, number, Article.NoArt)[0].value
        base_adj_form = adjective.to(Case.Nom, number, Article.NoArt)[0].value
        
        # Extract mutated noun and adjective forms
        print(noun, Case.Gen, number, Article.NoArt)
        mut_noun_form = noun.to(Case.Gen, number, Article.NoArt)[0].value
        print(adjective, Case.Gen, number, Article.NoArt)
        mut_adj_form = adjective.to(Case.Gen, number, Article.NoArt)[0].value
        
        # Analyze mutations
        noun_mut_front, noun_mut_mid, noun_mut_back = self.analyze_mutation(base_noun_form, mut_noun_form)
        adj_mut_front, adj_mut_mid, adj_mut_back = self.analyze_mutation(base_adj_form, mut_adj_form)
        
        return AdjectiveExample(
            name=adjective_key,
            prefix=prep_prefix,
            article=article_base,
            article_mut=article_mut,
            noun=base_noun_form,
            noun_mut_front=noun_mut_front,
            noun_mut_mid=noun_mut_mid,
            noun_mut_back=noun_mut_back,
            adjective=base_adj_form,
            adj_mut_front=adj_mut_front,
            adj_mut_mid=adj_mut_mid,
            adj_mut_back=adj_mut_back
        )
    
    def generate_random_examples(self, count: int) -> List[AdjectiveExample]:
        """
        Generate a list of random adjective examples.
        
        Args:
            count: Number of examples to generate
            
        Returns:
            List of AdjectiveExample objects
        """
        examples = []
        
        # Common Irish prepositions that cause mutations
        mutation_prefixes = [
            "i ndiaidh",  # after
            "in aice",    # beside
            "os comhair", # in front of
            "ar feadh",   # for (duration)
            "de bharr",   # because of
            "i gcóir",    # for/towards
            None,         # no prefix (genitive case)
        ]
        
        for i in range(count):
            # Select random components
            noun_key = choice(self.nouns)
            adj_key = choice(self.adjectives)
            prefix = choice(mutation_prefixes)
            with_article = choice([True, False])
            is_plural = choice([True, False])
            
            example = self.generate_example(
                noun_key, adj_key, prefix, with_article, is_plural
            )
            examples.append(example)
        
        return examples


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
    Main function to generate adjective examples.
    
    Args:
        data_folder: Path to the Gramadán data folder
    """
    # Load grammatical data
    print("Loading Gramadán database...")
    dictionaries = load_gramadan_database(data_folder)
    
    # Initialize generator
    generator = AdjectiveGenerator(dictionaries)
    
    # Generate examples
    print(f"Generating {SAMPLES} adjective examples...")
    examples = generator.generate_random_examples(SAMPLES)
    
    if not examples:
        print("No examples generated!")
        return
    
    # Convert to JSON format
    json_data = [example.to_dict() for example in examples]
    
    # Save to JSON file
    output_file = Path(ADJECTIVES_OUTPUT_FILE)
    print(f"Saving {len(json_data)} examples to {ADJECTIVES_OUTPUT_FILE}...")
    
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully generated {len(json_data)} adjective examples!")
    print(f"Sample example:")
    if json_data:
        sample = json_data[0]
        print(f"  Name: {sample['name']}")
        print(f"  Phrase: {sample['prefix']} {sample['article']} {sample['noun']} {sample['adjective']}")
        print(f"  Mutated: {sample['prefix']} {sample['articleMut']} " + 
              f"{sample['nounMutFront']}{sample['nounMutMid']}{sample['nounMutBack']} " +
              f"{sample['adjMutFront']}{sample['adjMutMid']}{sample['adjMutBack']}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_adjectives.py <gramadan_data_folder>")
        print("Example: python make_adjectives.py /path/to/gramadan/data")
        sys.exit(1)
    
    main(sys.argv[1])
