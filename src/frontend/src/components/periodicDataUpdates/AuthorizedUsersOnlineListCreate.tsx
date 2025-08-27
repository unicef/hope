import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import type { AuthorizedUser as APIAuthorizedUser } from '@restgenerated/models/AuthorizedUser';
import { useTranslation } from 'react-i18next';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import { BaseSection } from '@components/core/BaseSection';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  OutlinedInput,
  Chip,
  Grid2 as Grid,
} from '@mui/material';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { renderUserName } from '@utils/utils';

interface AuthorizedUsersOnlineListCreateProps {
  setFieldValue: (field: string, value: any, shouldValidate?: boolean) => void;
  selected: string[];
  setSelected: React.Dispatch<React.SetStateAction<string[]>>;
}

export const AuthorizedUsersOnlineListCreate: React.FC<
  AuthorizedUsersOnlineListCreateProps
> = ({ setFieldValue, selected, setSelected }) => {
  type AuthorizedUser = APIAuthorizedUser & {
    canEdit: boolean;
    canApprove: boolean;
    canMerge: boolean;
    name: string;
  };
  const { t } = useTranslation();
  const { businessAreaSlug, programSlug } = useBaseUrl();

  const [search, setSearch] = React.useState('');
  const [permission, setPermission] = React.useState<string[]>([]);

  const { data, isLoading, error } = useQuery({
    queryKey: ['availableUsers', businessAreaSlug, programSlug],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsUsersAvailableList(
        {
          businessAreaSlug: businessAreaSlug,
          programSlug: programSlug,
        },
      ),
    enabled: Boolean(businessAreaSlug && programSlug),
  });

  // Map API permissions to UI flags
  function mapPermissions(user: AuthorizedUser) {
    return {
      ...user,
      canEdit: user.pduPermissions.includes('PDU_ONLINE_SAVE_DATA'),
      canApprove: user.pduPermissions.includes('PDU_ONLINE_APPROVE'),
      canMerge: user.pduPermissions.includes('PDU_ONLINE_MERGE'),
      name: renderUserName(user),
    };
  }

  //@ts-ignore endpoint does not return data results
  const users: AuthorizedUser[] = data ? data.map(mapPermissions) : [];

  const filteredUsers = users.filter((user) => {
    const matchesSearch =
      user.name?.toLowerCase().includes(search.toLowerCase()) ||
      user.username?.toLowerCase().includes(search.toLowerCase()) ||
      false;
    if (!matchesSearch) return false;
    if (permission.length === 0) return true;
    return permission.some((perm) => {
      if (perm === 'canEdit') return user.canEdit;
      if (perm === 'canApprove') return user.canApprove;
      if (perm === 'canMerge') return user.canMerge;
      return false;
    });
  });

  const handleSelect = (userId: string) => {
    setSelected((prev) => {
      const newSelected = prev.includes(userId)
        ? prev.filter((sid) => sid !== userId)
        : [...prev, userId];
      setFieldValue('authorizedUsers', newSelected);
      return newSelected;
    });
  };

  if (isLoading) {
    return (
      <BaseSection title={t('Authorized Users Online')}>
        <Box>{t('Loading...')}</Box>
      </BaseSection>
    );
  }
  if (error) {
    return (
      <BaseSection title={t('Authorized Users Online')}>
        <Box color="error.main">{t('Failed to load authorized users.')}</Box>
      </BaseSection>
    );
  }

  return (
    <BaseSection
      description={t(
        'Select users who are allowed to perform actions (edit, approve and merge) for this template during online updates.',
      )}
      title={t('Authorized Users Online')}
    >
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid size={{ xs: 8 }}>
          <TextField
            label={t('Search')}
            variant="outlined"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            size="small"
            fullWidth
          />
        </Grid>
        <Grid size={{ xs: 4 }}>
          <FormControl size="small" sx={{ minWidth: 300 }} fullWidth>
            <InputLabel>{t('Permission Type')}</InputLabel>
            <Select
              label={t('Permission Type')}
              multiple
              value={permission}
              onChange={(e) => {
                const value = e.target.value;
                setPermission(
                  typeof value === 'string' ? value.split(',') : value,
                );
              }}
              input={<OutlinedInput label={t('Permission Type')} />}
              renderValue={(selectedPermissions) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selectedPermissions.length === 0
                    ? t('All')
                    : selectedPermissions.map((value: string) => (
                        <Chip
                          key={value}
                          label={
                            value === 'canEdit'
                              ? t('Authorized for Edit')
                              : value === 'canApprove'
                                ? t('Authorized for Approve')
                                : t('Authorized for Merge')
                          }
                        />
                      ))}
                </Box>
              )}
            >
              <MenuItem value="canEdit">{t('Authorized for Edit')}</MenuItem>
              <MenuItem value="canApprove">
                {t('Authorized for Approve')}
              </MenuItem>
              <MenuItem value="canMerge">{t('Authorized for Merge')}</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell></TableCell>
              <TableCell>{t('Users')}</TableCell>
              <TableCell>{t('Authorized for Edit')}</TableCell>
              <TableCell>{t('Authorized for Approve')}</TableCell>
              <TableCell>{t('Authorized for Merge')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredUsers.map((user) => (
              <TableRow key={user.id}>
                <TableCell>
                  <Checkbox
                    checked={selected.includes(user.id)}
                    onChange={() => handleSelect(user.id)}
                  />
                </TableCell>
                <TableCell>{user.name}</TableCell>
                <TableCell align="center">
                  {user.canEdit ? (
                    <CheckIcon color="success" />
                  ) : (
                    <CloseIcon color="disabled" />
                  )}
                </TableCell>
                <TableCell align="center">
                  {user.canApprove ? (
                    <CheckIcon color="success" />
                  ) : (
                    <CloseIcon color="disabled" />
                  )}
                </TableCell>
                <TableCell align="center">
                  {user.canMerge ? (
                    <CheckIcon color="success" />
                  ) : (
                    <CloseIcon color="disabled" />
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      {filteredUsers.length === 0 && (
        <Box sx={{ mt: 2 }}>{t('No authorized users found.')}</Box>
      )}
    </BaseSection>
  );
};
