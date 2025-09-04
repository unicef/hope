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
import { useParams } from 'react-router-dom';

interface AuthorizedUsersOnlineListEditProps {
  setFieldValue: (field: string, value: any, shouldValidate?: boolean) => void;
  selected: string[];
  setSelected: React.Dispatch<React.SetStateAction<string[]>>;
}

export const AuthorizedUsersOnlineListEdit: React.FC<
  AuthorizedUsersOnlineListEditProps
> = ({ setFieldValue, selected, setSelected }) => {
  type AuthorizedUser = APIAuthorizedUser & {
    canEdit: boolean;
    canApprove: boolean;
    canMerge: boolean;
    name: string;
  };
  const { t } = useTranslation();
  const { businessAreaSlug, programSlug } = useBaseUrl();
  const { id } = useParams<{ id: string }>();

  const [search, setSearch] = React.useState('');
  const [permission, setPermission] = React.useState<string[]>([]);

  // Fetch authorized users for the template (already selected)
  const {
    data: editData,
    isLoading: isEditLoading,
    error: editError,
  } = useQuery({
    queryKey: ['onlineEdit', businessAreaSlug, programSlug, id],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsRetrieve(
        {
          businessAreaSlug: businessAreaSlug,
          programSlug: programSlug,
          id: id ? Number(id) : undefined,
        },
      ),
    enabled: Boolean(businessAreaSlug && programSlug && id),
  });

  // Fetch all available users
  const {
    data: availableUsersData,
    isLoading: isAvailableLoading,
    error: availableError,
  } = useQuery({
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
  function mapPermissions(user) {
    return {
      ...user,
      canEdit: user.pduPermissions.includes('PDU_ONLINE_SAVE_DATA'),
      canApprove: user.pduPermissions.includes('PDU_ONLINE_APPROVE'),
      canMerge: user.pduPermissions.includes('PDU_ONLINE_MERGE'),
      name: renderUserName(user),
    };
  }

  // List of all available users (useMemo for stable reference)
  const users: AuthorizedUser[] = React.useMemo(() => {
    return availableUsersData
      ? //@ts-ignore endpoint does not return data results
        availableUsersData.map(mapPermissions)
      : [];
  }, [availableUsersData]);

  // List of already authorized user IDs for this template (useMemo for stable reference)
  const alreadyAuthorizedIds = React.useMemo(() => {
    return editData?.authorizedUsers
      ? editData.authorizedUsers.map((user) => user.id)
      : [];
  }, [editData]);

  // On mount or when users change, check checkboxes for already authorized users
  React.useEffect(() => {
    if (users.length > 0 && alreadyAuthorizedIds.length > 0) {
      setSelected(alreadyAuthorizedIds);
      setFieldValue('authorizedUsers', alreadyAuthorizedIds);
    }
  }, [users, alreadyAuthorizedIds, setSelected, setFieldValue]);

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

  if (isEditLoading || isAvailableLoading) {
    return (
      <BaseSection title={t('Authorized Users Online')}>
        <Box>{t('Loading...')}</Box>
      </BaseSection>
    );
  }
  if (editError || availableError) {
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
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: '100vh',
          minHeight: 0,
        }}
      >
        <Box sx={{ mb: 2 }}>
          <Grid container spacing={2}>
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
                  <MenuItem value="canEdit">
                    {t('Authorized for Edit')}
                  </MenuItem>
                  <MenuItem value="canApprove">
                    {t('Authorized for Approve')}
                  </MenuItem>
                  <MenuItem value="canMerge">
                    {t('Authorized for Merge')}
                  </MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Box>
        <Box
          sx={{
            flex: 1,
            minHeight: 0,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <TableContainer
            sx={{ flex: 1, minHeight: 0, height: '100%', overflowY: 'auto' }}
          >
            <Table stickyHeader>
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
        </Box>
      </Box>
    </BaseSection>
  );
};
