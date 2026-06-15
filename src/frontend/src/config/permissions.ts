import { PermissionsEnum } from '@restgenerated/models/PermissionsEnum';

export const PERMISSIONS = PermissionsEnum;

// Module prefixes matched as substrings by hasPermissionInModule (drawer menu)
export const PERMISSION_MODULES = {
  POPULATION: 'POPULATION',
  HOUSEHOLDS: 'HOUSEHOLDS',
  INDIVIDUALS: 'INDIVIDUALS',
  PM: 'PM',
  GRIEVANCES: 'GRIEVANCES',
  ACCOUNTABILITY: 'ACCOUNTABILITY',
  COMMUNICATION_MESSAGE: 'COMMUNICATION_MESSAGE',
  SURVEY: 'SURVEY',
} as const;

export const GRIEVANCES_VIEW_LIST_PERMISSIONS: string[] = [
  PERMISSIONS.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
  PERMISSIONS.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
  PERMISSIONS.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
  PERMISSIONS.GRIEVANCES_VIEW_LIST_SENSITIVE,
  PERMISSIONS.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
  PERMISSIONS.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
];

export const GRIEVANCES_VIEW_DETAILS_PERMISSIONS: string[] = [
  PERMISSIONS.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
  PERMISSIONS.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR,
  PERMISSIONS.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
  PERMISSIONS.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
  PERMISSIONS.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR,
  PERMISSIONS.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER,
];

export function hasPermissions(
  permission: string | string[],
  allowedPermissions: string[] | null,
): boolean {
  // checks to see if has one permission or at least one from the array
  if (!allowedPermissions || allowedPermissions === null) return false;
  if (Array.isArray(permission)) {
    return allowedPermissions.some((perm) => permission.includes(perm));
  }
  return allowedPermissions.includes(permission);
}

export function hasPermissionInModule(
  module: string,
  allowedPermissions: string[] | null,
): boolean {
  if (!allowedPermissions || allowedPermissions === null) return false;
  return allowedPermissions.some((perm) => perm.includes(module));
}

export function hasCreatorOrOwnerPermissions(
  generalPermission: string,
  isCreator: boolean,
  creatorPermission: string,
  isOwner: boolean,
  ownerPermission: string,
  allowedPermissions: string[] | null,
): boolean {
  // use where we have to check 3 different permissions, for ex. grievances
  if (!allowedPermissions || allowedPermissions === null) return false;
  return (
    allowedPermissions.includes(generalPermission) ||
    (isCreator && allowedPermissions.includes(creatorPermission)) ||
    (isOwner && allowedPermissions.includes(ownerPermission))
  );
}
