import React from 'react';
import { BaseSection } from '@components/core/BaseSection';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Checkbox,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { AuthorizePaymentPlansModal } from '@components/managerialConsole/AuthorizePaymentPlansModal';
import { UniversalMoment } from '@components/core/UniversalMoment';

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
          onAuthorize={(_, comment) => {
            return bulkAction.mutateAsync({
              ids: selectedAuthorized,
              action: 'AUTHORIZE',
              comment: comment,
            });
          }}
        />
      }
    >
      <Table>
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox">
              <Checkbox
                checked={allSelected && selectedAuthorized.length > 0}
                onClick={handleSelectAllAuthorized}
              />
            </TableCell>
            <TableCell>{t('Payment Plan ID')}</TableCell>
            <TableCell>{t('Programme Name')}</TableCell>
            <TableCell>{t('Last Modified Date')}</TableCell>
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
              <TableCell>{plan.unicef_id}</TableCell>
              <TableCell>{plan.program}</TableCell>
              <TableCell>
                <UniversalMoment>
                  {plan.last_approval_process_date}
                </UniversalMoment>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </BaseSection>
  );
};
