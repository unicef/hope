import { Filter } from '@utils/utils';

/**
 * The option shape rendered by the REST autocomplete filters. Each filter maps
 * its backing list model down to this common `{ id, name }` pair.
 */
export interface AutocompleteOption {
  id: string;
  name: string;
}

/**
 * Props shared by the REST autocomplete filter components. Individual filters
 * intersect this with their own extras (e.g. `label`, `additionalVariables`)
 * and may relax required fields to optional where their callers omit them.
 */
export interface BaseAutocompleteFilterProps {
  disabled?: boolean;
  name: string;
  value?: string;
  filter?: Filter;
  initialFilter: Filter;
  appliedFilter: Filter;
  setAppliedFilter: (filter: Filter) => void;
  setFilter: (filter: Filter) => void;
  dataCy?: string;
}
