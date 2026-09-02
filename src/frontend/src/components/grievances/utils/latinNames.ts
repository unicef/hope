import camelCase from 'lodash/camelCase';

// Mirrors NAME_TO_LATIN_FIELDS in src/hope/apps/household/utils.py - the backend
// requires the *_latin twin of every changed name unless transliteration is enabled.
export const NAME_TO_LATIN_FIELDS = {
  given_name: 'given_name_latin',
  middle_name: 'middle_name_latin',
  family_name: 'family_name_latin',
  full_name: 'full_name_latin',
};

export const LATIN_NAME_FIELDS: string[] = Object.values(NAME_TO_LATIN_FIELDS);
export const NAME_FIELDS: string[] = Object.keys(NAME_TO_LATIN_FIELDS);

// Mirrors ascii_name_validator in src/hope/models/individual.py
export const LATIN_NAME_REGEX = /^[A-Za-z]+(?:[ '-][A-Za-z]+)*$/;

export const LATIN_NAME_FORMAT_ERROR =
  'Only ASCII letters, spaces, hyphens and apostrophes are allowed';

export function latinNameMissingError(latinFieldName: string): string {
  return `Provide ${latinFieldName} or enable automatic transliteration`;
}

// The backend transliterates on its own, so sending explicit latin values alongside
// the flag would silently win over it - drop them instead.
export function removeLatinNameFields<T extends Record<string, any>>(
  individualData: T,
): T {
  const result = { ...individualData };
  for (const latinField of LATIN_NAME_FIELDS) {
    delete result[camelCase(latinField)];
  }
  return result;
}

export function removeLatinNameRows(individualDataUpdateFields) {
  return (individualDataUpdateFields || []).filter(
    (item) => !LATIN_NAME_FIELDS.includes(item?.fieldName),
  );
}

export function hasNameFieldRow(individualDataUpdateFields): boolean {
  return (individualDataUpdateFields || []).some((item) =>
    NAME_FIELDS.includes(item?.fieldName),
  );
}

// Transliteration only applies when a name is actually being changed; otherwise a
// latin-only correction would be stripped from the payload and silently lost.
export function transliterateUpdateRows(values): boolean {
  return (
    Boolean(values.transliterateLatinNames) &&
    hasNameFieldRow(values.individualDataUpdateFields)
  );
}
