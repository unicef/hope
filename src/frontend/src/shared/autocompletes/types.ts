/**
 * The option shape rendered by the REST autocomplete filters. Each filter maps
 * its backing list model down to this common `{ id, name }` pair.
 */
export interface AutocompleteOption {
  id: string;
  name: string;
}
