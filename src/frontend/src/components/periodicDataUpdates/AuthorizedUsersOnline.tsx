import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import type { PaginatedAuthorizedUserList } from '@restgenerated/models/PaginatedAuthorizedUserList';
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

interface AuthorizedUsersOnlineProps {
  setFieldValue: (field: string, value: any, shouldValidate?: boolean) => void;
}

export const AuthorizedUsersOnline: React.FC<AuthorizedUsersOnlineProps> = ({
  setFieldValue,
}) => {
  // API model
  type AuthorizedUser = APIAuthorizedUser & {
    canEdit: boolean;
    canApprove: boolean;
    canMerge: boolean;
    name: string;
  };
  const { t } = useTranslation();

  // Fallback fake data for UI display
  const fakeData: APIAuthorizedUser[] = [
    {
      id: '1',
      firstName: 'Stefano',
      lastName: 'Examplo',
      username: 'stefano',
      email: 'stefano@example.com',
      pduPermissions: ['PDU_ONLINE_SAVE_DATA'],
    },
    {
      id: '2',
      firstName: 'Julie',
      lastName: 'Halding',
      username: 'julie',
      email: 'julie@example.com',
      pduPermissions: ['PDU_ONLINE_APPROVE'],
    },
    {
      id: '3',
      firstName: 'Jean',
      lastName: 'Wilner Bassette',
      username: 'jean',
      email: 'jean@example.com',
      pduPermissions: ['PDU_ONLINE_APPROVE'],
    },
    {
      id: '4',
      firstName: 'Michael',
      lastName: 'Jord',
      username: 'nikola',
      email: 'nikola@example.com',
      pduPermissions: ['PDU_ONLINE_MERGE'],
    },
    {
      id: '5',
      firstName: 'Name',
      lastName: '',
      username: 'name5',
      email: 'name5@example.com',
      pduPermissions: [],
    },
    {
      id: '6',
      firstName: 'Name',
      lastName: '',
      username: 'name6',
      email: 'name6@example.com',
      pduPermissions: [],
    },
  ];

  const { businessAreaSlug, programSlug } = useBaseUrl();

  const { data, isLoading, error } = useQuery<PaginatedAuthorizedUserList>({
    queryKey: ['authorizedUsersOnline', businessAreaSlug, programSlug],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsUsersAvailableList(
        {
          businessAreaSlug: businessAreaSlug || '',
          programSlug: programSlug || '',
        },
      ),
    enabled: Boolean(businessAreaSlug && programSlug),
  });

  const [search, setSearch] = React.useState('');
  const [permission, setPermission] = React.useState<string[]>([]);
  const [selected, setSelected] = React.useState<string[]>([]);

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

  //TODO: remove fake data when not needed
  let users: AuthorizedUser[] = [];
  if (data?.results && data.results.length > 0) {
    users = data.results.map(mapPermissions);
  } else {
    users = fakeData.map(mapPermissions);
  }

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

  const handleSelect = (id: string) => {
    setSelected((prev) => {
      const newSelected = prev.includes(id)
        ? prev.filter((sid) => sid !== id)
        : [...prev, id];
      setFieldValue('authorizedUserIds', newSelected);
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
