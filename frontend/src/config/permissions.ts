export const PERMISSIONS = {
  CREATE: 'CREATE',
  UPDATE: 'UPDATE',
  DELETE: 'DELETE',
  READ: 'READ',
  LIST: 'LIST',
  RUN: 'RUN',

  DASHBOARD: 'DASHBOARD',
  RDI_LIST: 'RDI',

  RDI_IMPORT: 'PERMISSION_RDI_IMPORT',
  RDI_RERUN_DEDUPLICATION: 'PERMISSION_RDI_RERUN_DEDUPLICATION',
  RDI_MERGE: 'PERMISSION_RDI_MERGE',
  RDI_KOBO: 'PERMISSION_RDI_KOBO',
  RDI_XLSX: 'PERMISSION_RDI_XLSX',
};

export function hasPermissions(
  permission: string[],
  allowedPermissions: string[],
): boolean {
  const stringPermission = permission.join('.');
  return allowedPermissions.includes(stringPermission);
}
