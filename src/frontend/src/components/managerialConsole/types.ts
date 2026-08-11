import { Dispatch, SetStateAction } from 'react';

/** Variables accepted by the managerial-console bulk-action mutation. */
export interface BulkActionVariables {
  ids: string[];
  action: string;
  comment: string;
}

/**
 * The slice of the TanStack `useMutation` result the sections actually use.
 * A full `UseMutationResult` is structurally assignable to this.
 */
export interface BulkActionMutation {
  mutateAsync: (variables: BulkActionVariables) => Promise<unknown>;
}

export type SelectHandler = (
  selected: string[],
  setSelected: Dispatch<SetStateAction<string[]>>,
  id: string,
) => void;

export type SelectAllHandler = (
  ids: string[],
  selected: string[],
  setSelected: Dispatch<SetStateAction<string[]>>,
) => void;
