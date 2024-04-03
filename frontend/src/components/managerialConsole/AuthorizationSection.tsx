import React from 'react';
import { BaseSection } from '@components/core/BaseSection';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Checkbox,
  Box,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { AuthorizePaymentPlansModal } from '@components/managerialConsole/AuthorizePaymentPlansModal';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useSnackbar } from '@hooks/useSnackBar';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface AuthorizationSectionProps {
  selectedAuthorized: any[];
  setSelectedAuthorized: (value: React.SetStateAction<any[]>) => void;
  handleSelect: (
    selected: any[],
    setSelected: (value: React.SetStateAction<any[]>) => void,
    id: any,
  ) => void;
  handleSelectAll: (
    ids: any[],
    selected: any[],
    setSelected: {
      (value: React.SetStateAction<any[]>): void;
      (arg0: any[]): void;
    },
  ) => void;
  inAuthorizationData: any;
  bulkAction: any;
}

export const AuthorizationSection: React.FC<AuthorizationSectionProps> = ({
  selectedAuthorized,
  setSelectedAuthorized,
  handleSelect,
  handleSelectAll,
  inAuthorizationData,
  bulkAction,
}) => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const handleSelectAllAuthorized = () => {
    const ids = inAuthorizationData.results.map((plan) => plan.id);
    return handleSelectAll(ids, selectedAuthorized, setSelectedAuthorized);
  };

  const allSelected = inAuthorizationData?.results?.every((plan) =>
    selectedAuthorized.includes(plan.id),
  );

  const selectedPlansUnicefIds = inAuthorizationData?.results
    .filter((plan) => selectedAuthorized.includes(plan.id))
    .map((plan) => plan.unicef_id);

  return (
    <BaseSection
      title={t('Payment Plans pending for Authorization')}
      buttons={
        <AuthorizePaymentPlansModal
          selectedPlansIds={selectedAuthorized}
          selectedPlansUnicefIds={selectedPlansUnicefIds}
          onAuthorize={async (_, comment) => {
            try {
              await bulkAction.mutateAsync({
                ids: selectedAuthorized,
                action: 'AUTHORIZE',
                comment: comment,
              });
              showMessage(t('Payment Plan(s) Authorized'));
              setSelectedAuthorized([]);
            } catch (e) {
              showMessage(e.message);
            }
          }}
        />
      }
    >
      <Table>
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox" style={{ width: '10%' }}>
              <Box sx={{ flex: 1 }}>
                <Checkbox
                  checked={allSelected && selectedAuthorized.length > 0}
                  onClick={handleSelectAllAuthorized}
                />
              </Box>
            </TableCell>
            <TableCell align="left" style={{ width: '22.5%' }}>
              <Box sx={{ flex: 1 }}>{t('Payment Plan ID')}</Box>
            </TableCell>
            <TableCell align="left" style={{ width: '22.5%' }}>
              <Box sx={{ flex: 1 }}>{t('Programme Name')}</Box>
            </TableCell>
            <TableCell align="left" style={{ width: '22.5%' }}>
              <Box sx={{ flex: 1 }}>{t('Last Modified Date')}</Box>
            </TableCell>
            <TableCell align="left" style={{ width: '22.5%' }}>
              <Box sx={{ flex: 1 }}>{t('Approved by')}</Box>
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {inAuthorizationData?.results?.map((plan: any) => (
            <TableRow key={plan.id}>
              <TableCell padding="checkbox">
                <Checkbox
                  checked={selectedAuthorized.includes(plan.id)}
                  onChange={() =>
                    handleSelect(
                      selectedAuthorized,
                      setSelectedAuthorized,
                      plan.id,
                    )
                  }
                />
              </TableCell>
              <TableCell align="left">
                <BlackLink
                  to={`/${businessArea}/programs/${plan.program_id}/payment-module/${plan.isFollowUp ? 'followup-payment-plans' : 'payment-plans'}/${plan.id}`}
                  newTab={true}
                >
                  {plan.unicef_id}
                </BlackLink>
              </TableCell>
              <TableCell align="left">{plan.program}</TableCell>
              <TableCell align="left">
                <UniversalMoment>
                  {plan.last_approval_process_date}
                </UniversalMoment>
              </TableCell>
              <TableCell align="left">
                {plan.last_approval_process_by}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </BaseSection>
  );
};
