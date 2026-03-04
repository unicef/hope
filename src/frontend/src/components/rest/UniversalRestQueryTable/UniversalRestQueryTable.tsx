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
  getTitle?: (data: any) => string;
  title?: string;
  isOnPaper?: boolean;
  defaultOrderBy?: string;
  defaultOrderDirection?: Order;
  actions?: Array<ReactElement>;
  onSelectAllClick?: (event: any, rows: any) => void;
  numSelected?: number;
  allowSort?: boolean;
  filterOrderBy?: string;
  onPageChanged?: (page: number) => void;
  queryVariables: any;
  setQueryVariables: (variables: K) => void;
  itemsCount?: number;
  query: (variables: K) => Promise<any>;
  page?: number;
  setPage?: (page: number) => void;
  customEnabled?: boolean;
}

export const UniversalRestQueryTable = <T, K>(
  props: UniversalRestQueryTableProps,
): ReactElement => {
  const { query, page, setPage, customEnabled = true, ...propsToPass } = props;
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
    enabled: customEnabled && !!businessArea && !!programSlug,
  });
  return (
    <UniversalRestTable<T, K>
      {...propsToPass}
      page={page}
      setPage={setPage}
      data={data}
      isLoading={isLoading}
      error={error}
    />
  );
};
