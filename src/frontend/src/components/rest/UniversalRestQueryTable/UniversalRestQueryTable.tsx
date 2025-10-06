import { ReactElement } from 'react';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { HeadCell } from '@core/Table/EnhancedTableHead';
import { Order } from '@components/rest/TableRestComponent/TableRestComponent';
import { isUndefined, omitBy } from 'lodash';

interface UniversalRestQueryTableProps<T = any, K = any> {
  rowsPerPageOptions?: number[];
  renderRow: (row: T) => ReactElement;
  headCells: HeadCell<T>[];
  getTitle?: (data: any) => string; //TODO MS: add correct type for data
  title?: string;
  isOnPaper?: boolean;
  defaultOrderBy?: string;
  defaultOrderDirection?: Order;
  actions?: Array<ReactElement>;
  onSelectAllClick?: (event: any, rows: any) => void; //TODO MS: add correct types for event and rows
  numSelected?: number;
  allowSort?: boolean;
  filterOrderBy?: string;
  onPageChanged?: (page: number) => void;
  //TODO MS: add correct types
  queryVariables: any;
  setQueryVariables: (variables: K) => void;
  itemsCount?: number;
  query: (variables: K) => Promise<any>;
}

export const UniversalRestQueryTable = <T, K>(
  props: UniversalRestQueryTableProps,
): ReactElement => {
  const { query, ...propsToPass } = props;
  const { businessArea, programSlug } = useBaseUrl();
  const { queryVariables } = props;
  const cleanedQueryVariables = omitBy(queryVariables, isUndefined);
  const { data, isLoading, error } = useQuery({
    queryKey: [query.name, cleanedQueryVariables, programSlug, businessArea],
    queryFn: () =>
      query({
        businessAreaSlug: businessArea,
        programSlug,
        ...cleanedQueryVariables,
      }),
    enabled: !!businessArea && !!programSlug,
  });
  return (
    <UniversalRestTable<T, K>
      {...propsToPass}
      data={data}
      isLoading={isLoading}
      error={error}
    />
  );
};
