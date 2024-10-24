import { AllPaymentsForTableQuery } from '@generated/graphql';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { PERMISSIONS } from '../../../../config/permissions';

export const headCells: HeadCell<
  AllPaymentsForTableQuery['allPayments']['edges'][number]['node']
>[] = [
  {
    disablePadding: false,
    label: '',
    id: 'flag',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Payment ID',
    id: 'unicef_id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household ID',
    id: 'household__unicef_id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household Size',
    id: 'household__size',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Administrative Level 2',
    id: 'household__admin2__name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Collector',
    id: 'collector_id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'FSP',
    id: 'financial_service_provider__name',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Entitlement',
    id: 'entitlement_quantity_usd',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Delivered Quantity',
    id: 'delivered_quantity',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'FSP Auth Code',
    id: 'fsp_auth_code',
    numeric: false,
    requiredPermission: PERMISSIONS.PM_VIEW_FSP_AUTH_CODE,
  },
  {
    disablePadding: false,
    label: 'Reconciliation',
    id: 'mark',
    numeric: false,
  },
];
