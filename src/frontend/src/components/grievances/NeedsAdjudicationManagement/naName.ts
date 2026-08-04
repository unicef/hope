/**
 * Splits a full name into given/family parts, treating the last whitespace
 * separated token as the family name.
 *
 * TODO: this is a stopgap. IndividualForTicketSerializer
 * (src/hope/apps/household/api/serializers/individual.py) sends only
 * `full_name`, so the split has to be guessed here, and the guess is wrong
 * wherever the family name comes first. Once the serializer sends `given_name`
 * and `family_name`, NaComparisonPanel prefers those and this helper only
 * covers older payloads.
 */
export const splitFullName = (
  fullName: string | null | undefined,
): { givenName: string; familyName: string } => {
  const tokens = (fullName ?? '').trim().split(/\s+/).filter(Boolean);
  if (tokens.length === 0) return { givenName: '', familyName: '' };
  if (tokens.length === 1) return { givenName: '', familyName: tokens[0] };
  return {
    givenName: tokens.slice(0, -1).join(' '),
    familyName: tokens[tokens.length - 1],
  };
};
