export const PERMISSIONS = {
  // RDI
    RDI_VIEW_LIST: 'RDI_VIEW_LIST',
    RDI_VIEW_DETAILS: 'RDI_VIEW_DETAILS',
    RDI_IMPORT_DATA: 'RDI_IMPORT_DATA',
    RDI_RERUN_DEDUPE: 'RDI_RERUN_DEDUPE',
    RDI_MERGE_IMPORT: 'RDI_MERGE_IMPORT',

    // Population
    POPULATION_VIEW_HOUSEHOLDS_LIST: 'POPULATION_VIEW_HOUSEHOLDS_LIST',
    POPULATION_VIEW_HOUSEHOLDS_DETAILS: 'POPULATION_VIEW_HOUSEHOLDS_DETAILS',
    POPULATION_VIEW_INDIVIDUALS_LIST: 'POPULATION_VIEW_INDIVIDUALS_LIST',
    POPULATION_VIEW_INDIVIDUALS_DETAILS: 'POPULATION_VIEW_INDIVIDUALS_DETAILS',

    // User Management
    USER_MANAGEMENT_VIEW_LIST: 'USER_MANAGEMENT_VIEW_LIST'
};

export function hasPermissions(permission: string | string[], allowedPermissions: string[]): boolean {
// checks to see if has one permission or at least one from the array

  if (Array.isArray(permission)) {
    return allowedPermissions.some(perm => permission.includes(perm));
  }
  return allowedPermissions.includes(permission)
}

export function hasPermissionInModule(module: string, allowedPermissions: string[]): boolean {
  return allowedPermissions.some(perm => perm.includes(module))
}


