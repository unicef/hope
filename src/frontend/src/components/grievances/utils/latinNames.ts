export const LATIN_NAME_FIELDS = [
  'given_name_latin',
  'middle_name_latin',
  'family_name_latin',
  'full_name_latin',
];

// Mirrors ascii_name_validator in src/hope/models/individual.py
export const LATIN_NAME_REGEX = /^[A-Za-z]+(?:[ '-][A-Za-z]+)*$/;

export const LATIN_NAME_FORMAT_ERROR =
  'Only ASCII letters, spaces, hyphens and apostrophes are allowed';
