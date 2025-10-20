import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { PaymentList } from '@restgenerated/models/PaymentList';
import { PERMISSIONS } from '../../../../config/permissions';

export const headCells: HeadCell<PaymentList>[] = [
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
    label: 'Individual ID',
    id: 'individual__unicef_id',
    numeric: false,
    disableSort: true,
  },
  {
    disablePadding: false,
    label: 'Individual Name',
    id: 'individual__full_name',
    numeric: false,
    disableSort: true,
  },
  {
    disablePadding: false,
    label: 'Administrative Level 2',
    id: 'household__admin2__name',
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
    label: 'Status',
    id: 'status',
    numeric: false,
    disableSort: true,
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
